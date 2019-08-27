# importing the necessary library to make the call
import requests

def main ():
    url = "http://httpbin.org/xml"
    result = requests.get(url)
    printResult(result)

def printResult(resData):
    print("Status Code: {0}".format(resData.status_code))

    print ("Header ---------")
    print(resData.headers)
    print("\n")
    print("Returned Data ----------")
    print(resData.text)


if __name__ == "__main__":
    main()

