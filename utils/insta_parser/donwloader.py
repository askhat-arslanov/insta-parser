import asyncio
import os

import aiofiles

from .constants import ARCHIVES_DIR


async def download_single(url, account_name, session, sem, ws):
    async with sem:
        async with session.get(url) as response:
            filename = os.path.basename(url)
            async with aiofiles.open(
                os.path.join(
                    ARCHIVES_DIR, account_name, filename
                ), mode='wb'
            ) as f_handle:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    await f_handle.write(chunk)
            await ws.send_json({'state': 'download-increase'})
            return await response.release()


async def download_media(urls, account_name, session, ws):
    # Begin download notify
    await ws.send_json({'state': 'download'})
    # Create Semaphore instance for limit running courutine at the same time
    sem = asyncio.Semaphore(8)
    # Collect coroutines to execute
    await asyncio.gather(*(
        download_single(url, account_name, session, sem, ws) for url in urls
    ))
    # Download completed notify
    await ws.send_json({'state': 'download-completed'})
    