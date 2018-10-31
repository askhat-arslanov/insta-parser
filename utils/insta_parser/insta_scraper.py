import asyncio
import json
import re
from hashlib import md5

import aiohttp

from .constants import (
    INSTAGRAM_URL, NEXT_PAGE_URL, QUERY_PARAMETERS, QUERY_HASH, USER_AGENT)


def prepare_headers(insta_gis):
    return {
        "x-requested-with": "XMLHttpRequest",
        "x-instagram-gis": insta_gis,
        "user-agent": USER_AGENT
    }


async def get_next_page(session, csrf_token, insta_gis, query_hash, variables):
    """ Returns edges with media info and cursor for further query
    """
    cookies = {'csrftoken': csrf_token}
    # Add cookies to given session (aiohttp.ClientSession)
    session.cookie_jar.update_cookies(cookies)
    # And make headers
    headers = prepare_headers(insta_gis)
    # Create url 
    url = INSTAGRAM_URL + NEXT_PAGE_URL.format(
        query_hash=query_hash, variables=variables
    )
    response = await session.get(url, headers=headers)
    if response.status == 200:
        json_obj = await response.json()
        data = json_obj['data']['user']['edge_owner_to_timeline_media']
        end_cursor = data['page_info']['end_cursor']
        next_edges = data['edges']
        return next_edges, end_cursor
    elif response.status == 404:
        raise aiohttp.InvalidURL(url=url)
        

async def scraper(account, session, ws):
    """ Connects to instagram account, parses it
    and returns list of media urls
    """
    
    # Trying to connect notify
    await ws.send_json({'state': 'connection'})

    url = f'{INSTAGRAM_URL}/{account}/'
    async with session.get(
        url, headers={"user-agent": USER_AGENT}) as response:
        if response.status == 200:
            # Successful connection and begining parse notifies
            await ws.send_json({'state': 'connection-completed'})
            await ws.send_json({'state': 'parsing'})

            html = await response.text()
            # Find info about account from script in html
            json_str = re.search(
                r'window._sharedData = (.*);</script>', html).group(1)
            page_info = json.loads(json_str)
            # Extract user from JSON
            user_ = page_info['entry_data']['ProfilePage'][0]['graphql']['user']
            user_id = user_['id']
            # And other needful staff for further query
            end_cursor = user_['edge_owner_to_timeline_media']['page_info']['end_cursor']
            rhx_gis = page_info['rhx_gis']
            # Extract csrf token from cookie
            csrf_token = response.cookies.get('csrftoken')
            # Send user avatar and amount of media
            avatar = user_['profile_pic_url']
            total_media = user_['edge_owner_to_timeline_media']['count']
            user_info = {'avatar': avatar, 'total_media': total_media}
            await ws.send_json({'info': ('user-info', user_info)})

            # Get first 12 posts from home page
            edges = user_['edge_owner_to_timeline_media']['edges']
            # and notify about that by simple increase parsing iteration
            await ws.send_json({'state': 'parsing-increase'})

            # Get next posts to the end with a little bit tricky algorithm
            while end_cursor:
                # First of all make up right QUERY_PARAMETERS
                variables = QUERY_PARAMETERS.format(
                    user_id=user_id, end_cursor=end_cursor)
                # which pass with rhx_gis to md5 for hash
                insta_gis = md5(
                    (rhx_gis + ':' + variables).encode('utf-8')
                ).hexdigest()
                # And then pass it and other staff to get_next_page function,
                # which returns edges with media info for extract urls and
                # end_cursor for next query
                next_edges, end_cursor = await get_next_page(
                    session, csrf_token, insta_gis, QUERY_HASH, variables)
                edges.extend(next_edges)
                # Another increase parsing iteration notify
                await ws.send_json({'state': 'parsing-increase'})
                    
                # Take some break for decency
                await asyncio.sleep(2)

            # Parsing completed notify
            await ws.send_json({'state': 'parsing-completed'})
            # Extract media urls
            urls = [edge['node']['display_url'] for edge in edges]
            return urls

        elif response.status == 404:
            raise aiohttp.InvalidURL(url=url)
        