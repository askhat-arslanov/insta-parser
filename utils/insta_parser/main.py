import asyncio
import concurrent.futures
import os
import shutil

import aiohttp

from .archivist import prepare_archive
from .constants import ARCHIVES_DIR
from .donwloader import download_media
from .insta_scraper import scraper


async def parse_main(account_name, ws):
    async with aiohttp.ClientSession(
        cookie_jar=aiohttp.CookieJar()) as session:
        try:
            # Get media urls (and their amount) for further download 
            urls = await scraper(account_name, session, ws)
            # Create directory for certain account if it doesn't exist 
            path = os.path.join(ARCHIVES_DIR, account_name)
            if not os.path.exists(path):
                os.makedirs(path)
            # Donwload media
            await download_media(urls, account_name, session, ws)
            # Prepare fetched media to archive and delete temp
            # Begin prepared archive notify
            await ws.send_json({'state': 'prepared-archive'})
            loop = asyncio.get_event_loop()
            executor = concurrent.futures.ProcessPoolExecutor()
            file_name = await loop.run_in_executor(
                executor, prepare_archive, account_name)
            # Prepared archive end notify
            await ws.send_json({'state': 'prepared-archive-completed'})

        except aiohttp.InvalidURL:
            # if account wasn't founded notify user
            await ws.send_json({'state': 'not-found'})
            return 
        except Exception:
            await ws.send_json({'state': 'error'})
            return
        else: 
            await ws.send_json({'info': ('file-name', file_name)})
            # Remove zip file 20 minutes after creation
            await asyncio.sleep(20 * 60)
            if os.path.exists(path + '.zip'):
                os.remove(path + '.zip')
