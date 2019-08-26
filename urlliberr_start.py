import urllib.request
from http import HTTPStatus
from urllib.error import HTTPError


def main():
    url = "http://httpbin.org/status/404"
    result = urllib.request.urlopen(url)
    try:
        print("Hello There")
        print("Accessing : ", url)
        print("response code : {0}".format(result.status))
        if (result.getcode() == HTTPStatus.OK):
            print(result.read().decode('utf-8'))
    except HTTPError as err:
        print("Error : {0}".format(err.code))

if __name__ == "__main__":
    main()
