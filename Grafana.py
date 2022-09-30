#!/usr/bin/env python

import requests

header = {
            "Content-Type": "application/json"
        }

url = 'https://username:password@grafanaurl'

def mimir_tool(org_key):
    ------ Write YOur Code Here -----
    pass

def delete_api(api):
    try:
        response = requests.delete(url + api, headers=header).json()
        if response['message'] == 'API key deleted':
            return
        else:
            print('Something Went Wrong!')

    except Exception as e:
        print(e)


def create_api(api_get, api_create):

    response = requests.get(url + api_get, headers=header).json()
    response = [{i['id']: i['name']} for i in response]
    for i in response:
        for key,value in i.items():
            if value in ('api_key'):
                delete_api('/api/auth/keys/'+ key)

    payload = {
        "name": "api_key",
        "role": "Admin"
    }
    response = requests.post(url + api_create, json=payload, headers=header).json()
    return response['key']

def switch_org(api):
    response = requests.post(url + api, headers=header).json()

def current_org(api, id):
    response = requests.get(url + api, headers=header).json()
    if int(id) != int(response['id']):
        switch_org('/api/user/using/' + id)

def get_orgs(api):
    response = requests.get(url + api, headers=header).json()
    return [i['id'] for i in response]

def main():
    org_key = {}
    org_id = get_orgs('/api/orgs')
    for i in org_id:
        current_org('/api/org/', i)
        key = create_api('/api/auth/keys', '/api/auth/keys/')
        org_key[i] = key
    
    mimir_tool(org_key)

if __name__ == '__main__':
    main()
