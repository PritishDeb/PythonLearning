import urllib.request


def main():
    url = "http://httpbin.org/xml"
    result = urllib.request.urlopen(url)
    print("Hello There")
    print("Accessing : ", url)
    print("response code : {0}".format(result.status))

    print("Headers: -----------")
    #print(result.getheaders())

    print("Returned Data: -------------------")
    print(result.read().decode("utf-8"))


if __name__ == "__main__":
    main()
