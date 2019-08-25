import urllib.request
import urllib.parse


def main():
    url = "http://httpbin.org/get"
    args = {"name": "Pritish Debnath",
            "Profession": "Technology Consultant"}

    print("Hello There")
    print("Accessing : ", url)
    data = urllib.parse.urlencode(args)
    result = urllib.request.urlopen(url + "?" + data)
    print("response code : {0}".format(result.status))
    print("Headers: -----------")
    print(result.getheaders())

    print("Returned Data: -------------------")
    print(result.read().decode("utf-8"))


if __name__ == "__main__":
    main()
