# -*- coding: utf-8 -*-
import json
import pandas as pd
from os import listdir
from os.path import isfile, join

BASE_PATH = 'data'

def process_single_radar(id, lat, lng):
    radar_file = join(BASE_PATH, '{id}.json'.format(id=id))

    if isfile(radar_file):
        with open(radar_file, 'r') as radar_fd:
            raw_record = json.load(radar_fd)

            record = dict()
            record['date_heure_dernier_changement'] = raw_record['changed']
            record['date_heure_creation'] = raw_record['created']
            record['departement'] = raw_record['department'].split('-')[0].strip()
            record['latitude'] = lat
            record['longitude'] = lng
            record['id'] = raw_record['nid']
            record['direction'] = raw_record['radarDirection']
            record['equipement'] = raw_record['radarEquipment']
            record['date_installation'] = raw_record['radarInstallDate']
            record['type'] = raw_record['radarType'][0]['radarNameDetails']
            record['emplacement'] = raw_record['radarPlace']
            record['route'] = raw_record['radarRoad']

            # Parse radarTronconKm
            record['longueur_troncon_km'] = None
            if raw_record['radarTronconKm'] and raw_record['radarTronconKm'] != "-":
                record['longueur_troncon_km'] = float(raw_record['radarTronconKm'].replace(',', '.'))

            # Parse vitesse
            rules = [e['name'] for e in raw_record['rulesMesured']]

            vitesse_vl = [r for r in rules if r.startswith('Vitesse VL')]
            record['vitesse_vehicules_legers_kmh'] = None
            if len(vitesse_vl) == 1:
                record['vitesse_vehicules_legers_kmh'] = int(vitesse_vl[0].split(' ')[2].strip())

            vitesse_pl = [r for r in rules if r.startswith('Vitesse PL')]
            record['vitesse_poids_lourds_kmh'] = None
            if len(vitesse_pl) == 1:
                record['vitesse_poids_lourds_kmh'] = int(vitesse_pl[0].split(' ')[2].strip())

            return record
    return None


records = []
with open(join(BASE_PATH, '{id}.json'.format(id='___all___')), 'r') as all_radars_fd:
    for radar in json.load(all_radars_fd):
        try:
            record = process_single_radar(radar['id'], radar['lat'], radar['lng'])
            if record:
                records.append(record)
        except:
            print('Failure processing {id}'.format(id=radar['id']))
            raise

df = pd.DataFrame(records)
df['date_installation'] = pd.to_datetime(df['date_installation'])
for col in ['date_heure_dernier_changement', 'date_heure_creation']:
    df[col] = pd.to_datetime(df[col], unit='s')

df.sort_values(by=['id'], inplace=True)

df.to_csv(
    'data/radars.csv',
    index=False,
    encoding='utf-8',
    float_format='%.12g',
    date_format='%Y-%m-%dT%H:%M:%SZ'
)
