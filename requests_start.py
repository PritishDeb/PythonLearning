# importing the necessary library to make the call
import requests


def main():
    # We are using get method to get request from the url
    url = "http://httpbin.org/xml"
    result = requests.get(url)
    # printresult(result)


    # Post some data to the get endpoint using get method
    url = "http://httpbin.org/get"
    data = {
        "key1": "Value1",
        "key2": "Value2"
    }
    result = requests.get(url, params=data)
    #printresult(result)

    # Post some data to the get endpoint using post method
    url = "http://httpbin.org/post"
    data = {
        "key1": "Value1",
        "key2": "Value2"
    }
    result = requests.post(url, data=data)
    #printresult(result)

    # Post some data to the get endpoint using post method
    url = "http://httpbin.org/get"
    data = {
        "User": "Pritish Debnath",
    }
    result = requests.get(url, headers=data)
    printresult(result)


def printresult(resData):
    print("Status Code: {0}".format(resData.status_code))

    print("Header ---------")
    print(resData.headers)
    print("\n")
    print("Returned Data ----------")
    print(resData.text)


if __name__ == "__main__":
    main()
