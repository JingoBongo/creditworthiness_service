# import aiohttp
# import asyncio
# import time
#
# async def fetch(session, url, idx):
#     start_time = time.monotonic()
#     async with session.get(url) as response:
#         end_time = time.monotonic()
#         delay = end_time - start_time
#         print("Delay for request {}: {:.2f} seconds".format(idx, delay))
#         return delay < 1.0
#
# async def main():
#     urls = ["http://localhost:8000"] * 1000
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for idx, url in enumerate(urls):
#             task = asyncio.ensure_future(fetch(session, url, idx))
#             tasks.append(task)
#         results = await asyncio.gather(*tasks)
#
#         num_completed_in_time = sum(1 for result in results if result)
#         num_completed_late = len(results) - num_completed_in_time
#         print("Completed in time: {}, Completed late: {}".format(num_completed_in_time, num_completed_late))
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
from utils import git_utils, yaml_utils, general_utils
from utils import constants as c

# above is simple tester for how many requests endpoints can handle with what latency

# below will be yt dlp tests

number_of_screenshots = 5000
list_of_playlists = git_utils.get_yaml_file_from_repository(yaml_utils.get_cloud_repo_from_config(),
                                                            'youtube_playlists.yaml')['list']

dict_of_playlists_with_data = {}
for playlist in list_of_playlists:
    #   well, first we need length and size of each element of each playlist.. or just for playlists

    size_byte_res = general_utils.run_cmd_command_and_wait_response(
        f"yt-dlp --print \"%(filesize,filesize_approx)s\" -f \"bestvideo[height<=480]\" {playlist}")
    # 156 bytes per second for 480p video, roughly
    # therefore length = ALL_BYTES / 156
    # dict_of_playlists_with_data[playlist] = {}
    if '\\n' in str(size_byte_res): #then this is a list
        size_byte_res =sum([int(el.decode('utf-8')) for el in size_byte_res.split()])
    else:                           #then this is a single video
        size_byte_res = int(size_byte_res.decode('utf-8'))

    local_dict = {'size_b': size_byte_res,
                  'size_gb': size_byte_res / c.one_thousand_to_the_power_3,
                  'url': playlist,
                  'duration_seconds': int(size_byte_res / 41788)}
    dict_of_playlists_with_data[playlist] = local_dict
# here we should theoretically have all data about playlists
    total_seconds_available = 0
    playlists_to_download_list = []
    for playlist_dict in dict_of_playlists_with_data.values():
        temp_seconds = playlist_dict['duration_seconds']
        playlists_to_download_list.append(playlist_dict['url'])
        if total_seconds_available+temp_seconds > number_of_screenshots:
            break
        total_seconds_available += temp_seconds
print()