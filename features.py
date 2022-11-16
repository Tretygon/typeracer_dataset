import pandas as pd
import numpy as np
from collections import defaultdict
import operator

import keyboard
import scraper
import parse_log
import time

df:pd.DataFrame = scraper.load_mined()
df[['wpm','match','pos']] = df[['wpm','match','pos']].astype('int32')
df[['player']] = df[['player']].astype('string')
print(df.columns)
print(df['letters'].describe())

c = ['wpm','acc']
player_group = df.groupby('player')[c]
mn = df[c].sub(player_group.transform('mean'))
deviations = mn.add_suffix('_md')
print(deviations)

safe_get = lambda df,item: df.loc[item] if item in df.index else 0

def count_occurances(arrs):
    ret = defaultdict(lambda:0)
    for i,arr in arrs.items():
        for item in arr:
            ret[item] += 1
    return ret

def count_latencies(latencies,letters):
    ret = defaultdict(lambda:0)
    for (_,lat_arr),(_,let_arr) in zip(latencies.items(),letters.items()):
        for i,item in enumerate(let_arr):
            ret[item] += lat_arr[i]
    return ret



df['latencies'] = df['latencies'].apply(lambda arr:arr[1:])
df['mistake_letters'] = df.apply(lambda row: row['letters'][row['mistakes']], axis=1)
df['mistake_latencies'] = df.apply(lambda row: row['latencies'][row['mistakes']], axis=1)
print (df.dtypes)

mistake_count_dict = df['mistake_letters'].agg(count_occurances)
mistake_letters = pd.DataFrame(mistake_count_dict.items(),columns=['chr','occ']).set_index('chr')


mistake_latency_dict = count_latencies(df['mistake_latencies'],df['mistake_letters'])
mistake_latencies = pd.DataFrame(mistake_latency_dict.items(),columns=['chr','lat']).set_index('chr')


avg_misake_lat = mistake_latencies['lat']/mistake_letters['occ']

letter_occurances = df['letters'].agg(count_occurances)
letter_occurances = pd.DataFrame(letter_occurances.items(),columns=['chr','occ']).set_index('chr')


def ext_mistake_rates (chr_s,chr_us):
    lower_count = safe_get(letter_occurances,chr_us)
    upper_count = safe_get(letter_occurances,chr_s)
    total = upper_count + lower_count
    lower_mistakes= safe_get(mistake_letters,chr_us)
    upper_mistakes = safe_get(mistake_letters,chr_s)
    return (lower_mistakes + upper_mistakes)/total if total > 0 else 0
keyboard.show_heatmap(ext_mistake_rates,colormap = 'Oranges')

letter_latencies = count_latencies(df['latencies'],df['letters'])
letter_latencies = pd.DataFrame(letter_latencies.items(),columns=['chr','lat']).set_index('chr')
avg_letter_latencies = letter_latencies['lat']/letter_occurances['occ']

def ext (chr_s,chr_us):
    occs = letter_occurances['occ']
    get = lambda df,item: df.loc[item] if item in df.index else 0
    lower_count = get(occs,chr_us)
    upper_count = get(occs,chr_s)
    return upper_count + lower_count
keyboard.show_heatmap(ext,colormap = 'Oranges')
def ext (chr_s,chr_us):
    lats = letter_latencies['lat']
    occs = letter_occurances['occ']
    lower_lat = safe_get(lats,chr_us)
    lower_count = safe_get(occs,chr_us)
    upper_lat = safe_get(lats,chr_s)
    upper_count = safe_get(occs,chr_s)
    total_c = upper_count + lower_count
    return (lower_lat+upper_lat)/total_c if total_c > 0 else 0
keyboard.show_heatmap(ext,colormap = 'Oranges')

keypress_occurances = df.apply((lambda row: row['letters2'][(row['operations']==parse_log.press_type.Add_correct) * (row['operations']==parse_log.press_type.Add_mistake)]), axis=1)
backspace_counts = df.apply(lambda row: np.sum((row['operations']==parse_log.press_type.Remove_correct) * (row['operations']==parse_log.press_type.Remove_mistake)), axis=1)


required_keypresses = df.apply(lambda row: len(row['letters']), axis=1)
total_keypresses = df.apply(lambda row: len(row['operations']), axis=1)
total_mistakes = df.apply(lambda row: np.sum(row['mistakes']), axis=1)
print(required_keypresses)
print(total_keypresses)
print(total_mistakes)
extra_keypresses_per_mistake = (total_keypresses - required_keypresses)/total_mistakes
extra_keypresses_per_mistake = extra_keypresses_per_mistake.fillna(0)
print(extra_keypresses_per_mistake)
is_lowercase = letter_occurances.index.isin(keyboard.Row_infos.all_unshifted_combined)
lowercase_occ = letter_occurances[is_lowercase]
lowercase_latencies = letter_latencies[is_lowercase]

is_uppercase = letter_occurances.index.isin(keyboard.Row_infos.all_shifted_combined)
uppercase_occ = letter_occurances[is_uppercase]
uppercase_latencies = letter_latencies[is_uppercase]
avg_uppercase_latencies = avg_letter_latencies[is_uppercase]
avg_lowercase_latencies = avg_letter_latencies[is_lowercase]

avg_lowercase_latencies = pd.DataFrame(avg_lowercase_latencies)
avg_uppercase_latencies = pd.DataFrame(avg_uppercase_latencies)
avg_lowercase_latencies['key'] = lowercase_occ.index.map(lambda i:int(keyboard.Row_infos.all_unshifted_combined.index(i)))
avg_uppercase_latencies['key'] = uppercase_occ.index.map(lambda i:int(keyboard.Row_infos.all_shifted_combined.index(i)))

def ext (chr_s,chr_us):
    return avg_uppercase_latencies.loc[chr_s][0] if chr_s in avg_uppercase_latencies.index else 0
keyboard.show_heatmap(ext,colormap = 'Oranges')


def ext (chr_s,chr_us):
    return avg_lowercase_latencies.loc[chr_us][0] if chr_us in avg_lowercase_latencies.index else 0
keyboard.show_heatmap(ext,colormap = 'Oranges')

print(avg_lowercase_latencies.describe())
print(avg_uppercase_latencies.describe())
key_lat = avg_lowercase_latencies.merge(avg_uppercase_latencies,on='key',how='inner')
key_lat = key_lat.set_index('key')
key_lat = (key_lat['0_y']-key_lat['0_x'])
key_lat = pd.DataFrame(key_lat)
key_lat['letter'] = key_lat.index.map(lambda i:keyboard.Row_infos.all_unshifted_combined[i])
key_lat = key_lat.set_index('letter')

print(key_lat)
def ext (chr_s,chr_us):
    return key_lat.loc[chr_us][0] if chr_us in key_lat.index else 0
keyboard.show_heatmap(ext,colormap = 'Oranges')






print(df['mistake_letters'])
print(df['mistake_letters2'])

# df['mistake_latencies'] = df.apply(lambda row: row['latencies'][1:][np.logical_not(row['mistakes'])], axis=1)
# df['mistake_latencies2'] = df.apply(lambda row: row['latencies2'][row['operations']==parse_log.press_type.Add_correct], axis=1)
# print(df['latencies'])
# print(df['mistake_latencies2'])
'''

datamined from https://play.typeracer.com/
online typing game 
players are given a text and the task is to (correctly) type it as fast as possible
overall goal of this game is to improve ones typing skills - speed and accuracy

Data is limited to only english texts, 

~15% of replays were thrown out to keep the data clean
    - some parts of the typeracer replay has bugs (eg. characters get swapped, but it somehow pretends it didn't happened)
    - some rarer parts of the replay encoding evade my understanding
    - even though the text is in english, a few players use non-english layouts and can mistakenly write a non-asci char; this would make it hard to say what key was pressed

shift-key information is unfortunately not included


player: name of the player
match: 'kolikaty' match of the player played   (translation?????)
wpm: words per minute, a measure of typing speed
pos: at which position the player has placed (first=won, second, etc.)
acc: percentage of letters that were correctly written on the first try
letters: letters the text consisted of
latencies: time delay before each letter was correctly typed
mistakes: mistakes signifies whether letter was written correctly at the first try or not
letters_all: all letters typed and deleted (includes mistakes)
latencies_all: time delay before all keypresses
operations: operations[i] signifies whether letters_all[i] was: correctly typed, typed a mistake, deleted a mistake, deleted a correct letter
durations: how long each keypress lasted (keyboard buttons continuously send signal when pressed down)


dataset has one row per player playing a match
(does not consider the existence of the shift key)

possible annomalies: beginners have a huge time limit - oftentimes above 5 minutes, which can allow the player to take a long break 
on average off the general population only a few people use alternative keyboard layouts (eg.dvorak,colemak),
 however these people are also more likely to play typeracer. Information about the keyboard layout is by default not available to typeracer. 
 The only way to obtain this information is when the player specifies it. In such a case all races of those players were deliberately not collected.
'''

import keyboard
def cut_interval(vals,img,interval = 0.05):
    mn = vals[int(interval * len(vals))]
    mx = vals[int((1-interval) * len(vals))]
    img = np.where((img<=mn) * (img > 0),mn,img)
    img = np.where(img>=mx,mx,img)
    return img
keyboard.show_heatmap(key_freq,keyboard.extract_avg_latency,normalise_f=cut_interval)