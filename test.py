import vt
import urllib.parse


def IsConnectionFailed(url):
    try:
        urllib.request.urlopen(url)
    except Exception as e:
        print(e)
        return False
    return True


client = vt.Client(
    "62060697eabbc73532ff27b9f96625153f9b230d5f1a1f2fb4d2c241826ac423")

analysis = client.scan_url('https://google.com')
print(analysis.keys())
