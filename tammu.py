# importing packages
import requests
import lxml.html
from requests import HTTPError


def facebook(login_url, username, password):
    try:
        with requests.session() as s:
            result = s.get(login_url, allow_redirects=False)
            tree = lxml.html.fromstring(result.text)
            lsd = list(set(tree.xpath("//input[@name='lsd']/@value")))[0]
            jazoest = list(set(tree.xpath("//input[@name='jazoest']/@value")))[0]

            payload = {
                'email': username,
                'pass': password,
                'lsd': lsd,
                'jazoest': jazoest,
                'login': 'Log In'
            }

            result = s.post(login_url, data=payload, verify=False)

            # Login Successful if status code is 200
            if result.status_code == 200:
                print("Login was successful - Status Code {0}".format(result.status_code))
                nav_url = 'https://www.facebook.com/tamanna.agarwal.750'
                result = s.get(nav_url, verify=False)
                tree = lxml.html.fromstring(result.text)
                user = tree.xpath('//title[@id="pageTitle"]/text()')[0]
                print('User logged in:  {0}'.format(user))

            else:
                print("Login was unsuccessful - Status Code {0}".format(result.status_code))

    except HTTPError as err:
        print("Error: {0}".format(err))


def main():
    username = input("Enter your facebook username : ")
    password = input("Enter your facebook password : ")
    login_url = 'https://www.facebook.com/'

    facebook(login_url, username, password)


if __name__ == '__main__':
    main()
