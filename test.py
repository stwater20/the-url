import urllib.parse


def IsConnectionFailed(url):
    try:
        urllib.request.urlopen(url)
    except Exception as e:
        print(e)
        return False
    return True


print(IsConnectionFailed("https://sectools.tw/"))
