from bs4 import BeautifulSoup 
import requests
import pandas as pd
import seaborn as sb
import numpy as np
import re
import time
from datetime import datetime,timedelta
from collections import defaultdict
from enum import Enum
import itertools
import typing
from typing import Callable,Tuple
import parse_log
import pickle

req_interval = 0
last_req = datetime.now()
def get_page(req):
    address = 'https://data.typeracer.com/pit/' + req
    print(address)
    global last_req
    since_last_req = last_req -  datetime.now()
    # if  since_last_req < timedelta(seconds=req_interval):
    #     to_sleep = (timedelta(seconds=req_interval) - since_last_req)
    #     time.sleep(to_sleep.seconds)
    last_req = datetime.now()
    page  = requests.get(address)
    if page.status_code >= 400:
        print('request error ',req)
        time.sleep(15)
        return get_page(req)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    return soup



scraped = defaultdict(set) #remember what was already scraped to prevent pointless requests
data_header=['player','match','wpm','acc','pos', 'letters', 'frequencies','log2']
data =  pd.DataFrame(columns=data_header)

def zerozero(): #work around, so the dd can be pickled
    return (0,0)

key_freq = defaultdict(zerozero)

def save_mined():
    global data,scraped,key_freq,data_header
    data.to_csv('data.csv')
    pickle.dump( scraped, open( "scraped.p", "wb" ))
    pickle.dump( key_freq, open( "keys.p", "wb" ))
def load_mined():
    global data,scraped,key_freq,data_header
    data = pd.read_csv('data.csv')
    scraped = pickle.load(open( "scraped.p", "rb" ))
    key_freq = pickle.load(open( "keys.p", "rb" ))
    return data,key_freq

#load_mined()



def fetch_matches():
    global data,scraped,key_freq,data_header
    latest_races = get_page('latest')
    players = latest_races.find_all(class_="userProfileTextLink")
    duplicates = 0
    count_all = 0
    player_accessed = set()  #load each player only once in this function call; saves bunch of requests
    for p in players:
        print(f'dupes: {duplicates}, all: {count_all}, rate:{duplicates/count_all if count_all!=0 else 0}')
        href = p['href']
        p_name = href.split('?user=')[-1]
        
        
        count_all +=1
        if p_name in player_accessed: 
            duplicates+=1
            continue
        else: player_accessed.add(p_name)

        player_profile = get_page(href)
        if player_profile is None:continue

        #some limit data to only those, who use qwerty or havent specified their layout (=>probably qwerty users)
        kb_span = player_profile.find('span',string='Keyboard:')
        if kb_span != None and \
            kb_span.find_next_sibling('span').string != 'Qwerty':
            continue

        for a in player_profile.find_all('a',title="Click to see the replay"):
            match_href = a['href']
            player,match = match_href.split('|')[-2:]
            player = player.split(':')[-1]
            match = int(match)
            if match in scraped[player]:
                continue
            else:
                scraped[player].add(match)
            replay_page = get_page(match_href)
            # with open('rep_page','w') as f:
            #     f.write(str(replay_page))
            #     break
            if replay_page == None:
                print('no replay')
                continue
            info_table = replay_page\
                .find('td',string='Speed')
            if info_table == None:
                aa = str(replay_page)
                print()
            info_table = info_table.find_next_sibling()
            wpm = info_table\
                .span\
                .string\
                .split(' ')[0]
            wpm = int(wpm)
            info_table = info_table.findParent('tr').find_next_sibling('tr').findChildren('td')[-1]
            accuracy = info_table.string
            accuracy = float(accuracy[:accuracy.find('%')])
            info_table = info_table.findParent('tr').find_next_sibling('tr').findChildren('td')[-1]
            position = info_table.string[0]
            var_pattern = re.compile('var typingLog = \"')
            rem_pattern  = re.compile('( )*var typingLog = \"')
            

            typing_log = replay_page.find('script',string=var_pattern)
            if typing_log == None or len(typing_log)==0:
                print('no log')
                continue
            typing_log = re.sub(rem_pattern, '',typing_log.string.strip()[:-2])
            #print(typing_log)
            typing_log = typing_log.split('|')
            if len(typing_log)>2:
                continue
            else :
                parsed = parse_log.parse_typing_log1(typing_log[0])
                if parsed:
                    letters,latencies = parsed
                    
                    for lett,lat in zip(letters,latencies):
                        (occ,avg_lat) = key_freq[lett]
                        key_freq[lett] = (occ+1,avg_lat + (lat-avg_lat)/(occ+1))
                    #letters = np.array(letters)
                    #latencies = np.array(latencies)
                    row_dataset = pd.DataFrame([[player,match,wpm,accuracy,position,letters,latencies,typing_log[1]]],columns=data_header)
                    data = pd.concat([data,row_dataset],ignore_index=True,axis=0)
        save_mined()     
    return data



    #print(latencies)

if __name__ == '__main__':
    while True:
        fetch_matches()



