import aiohttp
import asyncio
import time

async def fetch(session, url, idx):
    start_time = time.monotonic()
    async with session.get(url) as response:
        end_time = time.monotonic()
        delay = end_time - start_time
        print("Delay for request {}: {:.2f} seconds".format(idx, delay))
        return delay < 1.0

async def main():
    urls = ["http://localhost:8000"] * 1000
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, url in enumerate(urls):
            task = asyncio.ensure_future(fetch(session, url, idx))
            tasks.append(task)
        results = await asyncio.gather(*tasks)

        num_completed_in_time = sum(1 for result in results if result)
        num_completed_late = len(results) - num_completed_in_time
        print("Completed in time: {}, Completed late: {}".format(num_completed_in_time, num_completed_late))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())