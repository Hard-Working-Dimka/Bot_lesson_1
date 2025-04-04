import requests
from environs import env
import httpx


def main():
    env.read_env()
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {env('DEVMAN_TOKEN')}',
    }

    payload = {}
    timestamp = None
    while True:

        try:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            response = response.json()

        except requests.exceptions.ReadTimeout:
            response = requests.get(url, headers=headers, params=payload)
        except requests.exceptions.ConnectionError:
            response = requests.get(url, headers=headers, params=payload)


        if response.get('last_attempt_timestamp'):
            timestamp = response['last_attempt_timestamp']
        if response.get('timestamp_to_request'):
            timestamp = response['timestamp_to_request']
        payload = {'timestamp': timestamp}
        print('___________________________')
        print(timestamp)


        print(response)


if __name__ == '__main__':
    main()
