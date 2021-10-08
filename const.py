from pymongo import MongoClient

regioes = {
    'Brazil': 'br1',
    'Korea': 'kr'
    #'North America': 'na1'
    #'Europe West': 'euw1',
    #'Europe Nordic & East': 'eun1'
}

conn = MongoClient('localhost', 27017)