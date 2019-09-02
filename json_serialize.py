import json


def main():
    pythondata = {
        "sandwich" : "Reuben",
        "toasted" : True,
        "toppings" : [
            "Thousand island dressing",
            "Sauerkraut",
            "Pickles"
        ],
        "Price" : 8.99
    }

    data = json.dumps(pythondata)
    print("Json Data: ----------")
    print(data)

if __name__ == "__main__":
    main()