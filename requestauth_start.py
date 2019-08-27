# importing the necessary library to make the call
import requests


def main():
    # Post some data to the get endpoint using post method
    url = "http://httpbin.org/basic-auth/pritish/password"
    mycreds = ("pritish","password")
    result = requests.get(url, auth=mycreds)
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
