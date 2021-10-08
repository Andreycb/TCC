import logging
import requests
import click
import os
import re

from const import conn
from time import sleep
from log import logger

api_key = ''

def first_objectives(dic, key, value='first'):
    if (dic[key][value]):
        return "Red Team"
    
    return "Blue Team"

def qtde_kills(team, obj, value='kills'):
    qtde = team[obj][value]
    return qtde

def read_mongodb_challangers():

    db = conn.Challangers
    collection = db.matches

    data = collection.find({ "BaronsBlueTeam": {"$exists": False}}, no_cursor_timeout=True)

    for index in data:
        id = index['id']
        id_region = re.search('[a-zA-z]{2}', id) 
        logger.info(f'Coletando informações sobre o jogo {id}')
        if id_region.group() == 'BR':
            region = 'americas'
        else:
            region = 'asia'

        
        link  = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{id}?api_key={api_key}'
        try:
            infos = requests.get(link)
            if infos.status_code == 429:
                while infos.status_code == 429:
                    logger.info('f{infos.status_code} TimeSleep')
                    sleep(30)
                    infos = requests.get(link)
        except requests.exceptions.ConnectionError:
            continue
        
        try:
            gameDuration = infos.json()['info']['gameDuration']

            blueteaminfo = infos.json()['info']['teams'][0]
            redteaminfo = infos.json()['info']['teams'][1]
            
            if (redteaminfo['win']):
                win = "Red Team"
            else:
                win = "Blue team"

            objectives_red = redteaminfo['objectives']
            objectives_blue = blueteaminfo['objectives']

            first_baron = first_objectives(objectives_red, 'baron')
            first_dragon = first_objectives(objectives_red, 'dragon')
            first_inhibtor = first_objectives(objectives_red, 'inhibitor')
            first_herold = first_objectives(objectives_red, 'riftHerald')
            first_tower = first_objectives(objectives_red, 'tower')

            qtde_baron_red = qtde_kills(objectives_red, 'baron')
            qtde_dragon_red = qtde_kills(objectives_red, 'dragon')
            qtde_inhibtor_red = qtde_kills(objectives_red, 'inhibitor')
            qtde_herold_red = qtde_kills(objectives_red, 'riftHerald')
            qtde_tower_red = qtde_kills(objectives_red, 'tower')
            qtde_baron_blue = qtde_kills(objectives_blue, 'baron')
            qtde_dragon_blue = qtde_kills(objectives_blue, 'dragon')
            qtde_inhibtor_blue = qtde_kills(objectives_blue, 'inhibitor')
            qtde_herold_blue = qtde_kills(objectives_blue, 'riftHerald')
            qtde_tower_blue = qtde_kills(objectives_blue, 'tower')
            

            data_up = { 'gameDuration' : gameDuration,
                     'win'          : win,
                     'FirstBaron'   : first_baron,
                     'FirstDragon'  : first_dragon,
                     'FirstInhibtor': first_inhibtor,
                     'FirstHerold'  : first_herold,
                     'FirstTower'   : first_tower,
                     'BaronsRedTeam': qtde_baron_red,
                     'DragonRedTeam': qtde_dragon_red,
                     'InhibtorsRedTeam' : qtde_inhibtor_red,
                     'TowerRedTeam' : qtde_tower_red,
                     'HeroldsRedTeam': qtde_herold_red,                
                     'BaronsBlueTeam': qtde_baron_blue,
                     'DragonBlueTeam': qtde_dragon_blue,
                     'InhibtorsBlueTeam' : qtde_inhibtor_blue,
                     'TowerBlueTeam' : qtde_tower_blue,
                     'HeroldsBlueTeam': qtde_herold_blue
                     }


            collection.update({"_id": index['_id']},{"$set" : data_up})
        except Exception as e:
            haha = infos.status_code
            logger.info(f'jogo {id} deu error {e} status_code {haha}')
            continue
    data.close()


@click.command(help='')
def run():
    read_mongodb_challangers()


if __name__ == '__main__':
    run()