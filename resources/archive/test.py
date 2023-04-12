import requests

pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'


def try_site(url):
    request = requests.get(url)
    print(request.status_code == 200)
    return False if pattern in request.text else True


# print(try_site("https://youtu.be/dQw4w9WgXcQ"))
print(try_site("https://youtube.com/playlist?list=PLyUciAhyXU08h0dYrl18YbttnTm16g3s9"))