# importing the necessary library to make the call
import requests
from requests import HTTPError, Timeout


def main():
    # We are using get method to get request from the url
    try:
        #url = "http://httpbin.org/status/404"
        url = "http://httpbin.org/delay/5"
        result = requests.get(url, timeout=2)
        result.raise_for_status()
        printresult(result)
    except HTTPError as err:
        print ("Error : {0}".format(err))
    except Timeout as err:
        print ("Requests timesout : {0}".format(err))


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
    #printresult(result)


def printresult(resData):
    print("Status Code: {0}".format(resData.status_code))

    print("Header ---------")
    print(resData.headers)
    print("\n")
    print("Returned Data ----------")
    print(resData.text)


if __name__ == "__main__":
    main()
