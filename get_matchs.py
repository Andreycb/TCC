import requests
import click
import os

from const import conn
from log import logger
from time import sleep

api_key = ''

def save_mongodb_matches(matches):

    db = conn.Challangers
    collection = db.matches
    
    matches_info = [   {"id": match
            }  
            for match in matches.json()]

    logger.info("Dicionario montado")
    for info in matches_info:
        try:
            cursor = collection.find(info,no_cursor_timeout=True).count()
            if not cursor:
                collection.insert_one(info)
            cursor.close()
        except:
            continue

def read_mongodb_challangers():

    db = conn.Challangers
    collection = db.challangers

    aux = collection.find({}, no_cursor_timeout=True)
    for rec in aux:
        puuid = str(rec['puuid'])
        init = 0

        if str(rec['region']) == 'br1':
            region = 'americas'
        else:
            region = 'asia'
        

        while True:
            link = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?api_key={api_key}&type=ranked&start={init}&count=100'
            matches = requests.get(link)

            if matches.status_code == 429:
                    sleep(120)
                    matches = requests.get(link)
            
            if len(matches.json()) == 0:
                break
            
            init += 100
            save_mongodb_matches(matches)

    aux.close()       
    

@click.command(help='')
def run():
    read_mongodb_challangers()


if __name__ == '__main__':
    run()