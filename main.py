# -*- coding: utf-8 -*-
import json
import requests
import urllib3

from tqdm import tqdm
from requests.adapters import HTTPAdapter

# Disable InsecureRequestWarning: Unverified HTTPS request is being made to host
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def endpoint(part):
    return 'https://{base}/{part}?_format=json'.format(
        base='radars.securite-routiere.gouv.fr/radars',
        part=part
    )


def do_request(session, url):
    request = session.get(
        url,
        verify=False,
        headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
    )
    request.raise_for_status()

    return request


if __name__ == "__main__":
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=5))
    radars = do_request(s, endpoint('all'))

    with open('data/___all___.json', 'w') as f:
        f.write(json.dumps(radars.json(), indent=4))

    for radar in tqdm(radars.json()):
        radar_id = radar['id']

        r = do_request(endpoint(radar_id))
        r.raise_for_status()

        path = 'data/{radar_id}.json'.format(radar_id=radar_id)
        with open(path, 'w') as f:
            f.write(json.dumps(r.json(), indent=4))
