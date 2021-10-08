import requests
import click
import os

from time import sleep
from const import regioes, conn
from log import logger

PROJECT_ROOT = os.path.dirname(__file__)
api_key = ''

def get_challanger(api_challenger):
    r = requests.get(api_challenger)
    r = [{"summonerId": d["summonerId"]} for d in r.json()['entries']]
    return r

def get_account_id(league, region):
    for code in league:
        try:
            summonerId = code['summonerId']
            profile = requests.get('https://'+str(region)+'.api.riotgames.com/lol/summoner/v4/summoners/'+summonerId+'?api_key='+api_key)
            
            if profile.status_code == 429:
                sleep(120)
                profile = requests.get('https://'+str(region)+'.api.riotgames.com/lol/summoner/v4/summoners/'+summonerId+'?api_key='+api_key)

            accountId = profile.json()['accountId']
            teste = requests.get('https://'+str(region)+'.api.riotgames.com/lol/summoner/v4/summoners/by-account/'+accountId+'?api_key='+api_key)
            if teste.status_code == 429:
                sleep(120)
                teste = requests.get('https://'+str(region)+'.api.riotgames.com/lol/summoner/v4/summoners/by-account/'+accountId+'?api_key='+api_key)

            code['puuid'] = teste.json()['puuid']
            code['accountId'] = accountId
            code['region'] = region

            save_mongodb(code)
        except:
            logger.exception(f"Exception: {profile.status_code}")
            continue

def save_mongodb(data):
        db = conn.Challangers
        collection = db.challangers
        collection.insert_one(data)
        conn.close()

@click.command(help='')
def run():
    for name, cod in regioes.items():
        link = f'https://{cod}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
        get_account_id(get_challanger(link), region=cod)


if __name__ == '__main__':
    run()