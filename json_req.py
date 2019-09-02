import json
import requests
from json import JSONDecodeError

def main():
    url = "http://httpbin.org/json"
    result = requests.get(url)
    print(result)

    try:
        dataobj = result.json()
        print(json.dumps(dataobj, indent=4))
        #accessing the keys of the dataobj
        print(list(dataobj.keys()))
        print(dataobj['slideshow']['author'])
        print("There are {0} slides ".format(len(dataobj['slideshow']['slides'])))

    except JSONDecodeError as err:
        print("Oops there is an error in the code: ")
        print(err.msg)



if __name__ == '__main__':
    main()