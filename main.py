# -*- coding: utf-8 -*-
import json
import requests
import urllib3

from tqdm import tqdm
from requests.adapters import HTTPAdapter

# Disable InsecureRequestWarning: Unverified HTTPS request is being made to host
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=5))


def endpoint(part):
    return 'https://{base}/{part}?_format=json'.format(
        base='radars.securite-routiere.gouv.fr/radars',
        part=part
    )


def do_request(url):
    r = s.get(
        url,
        verify=False,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
    )
    r.raise_for_status()

    return r


radars = do_request(endpoint('all'))
radars.raise_for_status()

with open('data/___all___.json', 'w') as f:
    f.write(json.dumps(radars.json(), indent=4))

for radar in tqdm(radars.json()):
    id = radar['id']

    r = do_request(endpoint(id))
    r.raise_for_status()

    path = 'data/{id}.json'.format(id=id)
    with open(path, 'w') as f:
        f.write(json.dumps(r.json(), indent=4))
