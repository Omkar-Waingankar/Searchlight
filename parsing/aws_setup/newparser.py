#initialization

import pandas as pd
import re
import numpy as np
import urllib
from bs4 import BeautifulSoup as Soup
import os
from pathlib import Path

#master mods parsing methods

def get_all_extensions(file):
    handler = open(file).read()
    soup = Soup(handler, "lxml")
    return soup.find_all("extension")

def get_cong_member_tag(cong_member_extension):
    cong_member_tag = cong_member_extension.find("congmember")
    return cong_member_tag

def get_party(cong_member_tag):
    try:
        return cong_member_tag.attrs['party']
    except:
        return 'N/A'

def get_type(cong_member_tag):
    try:
        return cong_member_tag.attrs['type']
    except:
        return 'N/A'

def get_authority_id(cong_member_tag):
    try:
        return cong_member_tag.attrs['authorityid']
    except:
        print("auth id not found")
        return None

def get_bioguide_id(cong_member_tag):
    try:
        return cong_member_tag.attrs['bioguideid']
    except:
        return 'N/A'

def get_state(cong_member_tag):
    try:
        return cong_member_tag.attrs['state']
    except:
        return 'N/A'

def get_congress_id(cong_member_tag):
    try:
        return cong_member_tag.attrs['congress']
    except:
        return 'N/A'

def get_chamber(cong_member_tag):
    chambers = {'S': 'SENATE', 'H': 'HOUSE'}
    try:
        letter = cong_member_tag.attrs['chamber']
        return chambers[letter]
    except:
        return 'N/A'

def get_district(cong_member_extension):
    district_tag = cong_member_extension.find("district")
    if district_tag == None:
        return None
    return district_tag.string

def get_first_name(cong_member_tag):
    name_tag_arr = cong_member_tag.select("name[type='authority-fnf']")
    if name_tag_arr == []:
        print("no first_name")
        print(cong_member_tag)
        return 'N/A'
    name_tag = name_tag_arr[0]
    first_name = name_tag.text.split()[0]
    return first_name

def get_last_name(cong_member_tag):
    name_tag_arr = cong_member_tag.select("name[type='authority-lnf']")
    if name_tag_arr == []:
        print("no first_name")
        print(cong_member_tag)
        return 'N/A'
    name_tag = name_tag_arr[0]
    full_name = name_tag.string
    return re.match("[^,]*", full_name).group(0).upper()

def remove_space(regex):
    return regex.group().replace(' ', '')

def sep_speech(filepath):
    parse_file = ''
    with open(filepath) as file:
        for line in file:
            parse_file += line
    parse_file = parse_file.replace('\n', '')
    parse_file = re.sub('Mr. [A-Z][a-z]', remove_space, parse_file)
    
    split = re.split(r'Mr. |Ms. |Mrs. ', parse_file)
    split.pop(0)
    name_and_speech = []
    for i in np.arange(len(split)):
        try:
            lastname = re.match('[A-Z]*\. ', split[i]).group(0)[:-2]
            name_and_speech += [lastname]
            value = re.sub('[A-Z]\w*\. ', '', split[i])
            name_and_speech += [value]
        except:
            continue
    return name_and_speech

def sep_date_from_file(file):
    abcdef = re.findall('[0-9]{4}-[0-9]{2}-[0-9]{2}', file)
    return re.split('-', abcdef[0])

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def find_title(file_path):
    parse_file = ''
    with open(file_path) as file:
        for line in file:
            parse_file += line
    parse_file = parse_file.replace('Mr. President', 'MrPresident')
    titles = re.findall('[A-Z \'-]+[A-Z0-9-,\. ]*[Continued]*\\n', parse_file)
    if is_int(titles[0].strip().replace('\n', '')):
        return titles[1].strip()
    else:
        return titles[0].strip()

def fix_surname_typos(name):
    if name == 'SOUZZI':
        return 'SUOZZI'
    if name == 'VANHOLLEN':
        return 'VAN HOLLEN'
    if name == 'FISHCER':
        return 'FISCHER'
    if name == 'MERKELY':
    	return 'MERKLEY'
    if name == 'BLUMENTAL':
    	return 'BLUMENTHAL'
    return name

#local mods parsing

def get_cong_member_tag_from_mods(last_name, mods_file_path):
    try:
        handler = open(mods_file_path).read()
    except:
        return None
    soup = Soup(handler, "lxml")
    cong_member_tags = soup.find_all("congmember")
    matched_cong_member_tag = None
    for i in range(len(cong_member_tags)):
        curr_last_name = get_last_name(cong_member_tags[i])
        if curr_last_name == last_name:
            matched_cong_member_tag = cong_member_tags[i]
            break
    return matched_cong_member_tag

def get_cong_member_info(last_name, mods_file_path):
    matched_cong_member_tag = get_cong_member_tag_from_mods(last_name, mods_file_path)
    if matched_cong_member_tag == None:
        return {'speaker_id': None, 
                'first_name': 'N/A',
                'last_name': last_name,
                'type': 'N/A',
                'chamber': 'N/A',
                'party': 'N/A',
                'state': 'N/A',
                'district': None,
                'bio_guide_id': 'N/A',
                'congress_id': 'N/A'}
    else:
        return {'speaker_id': get_authority_id(matched_cong_member_tag), 
                'first_name': get_first_name(matched_cong_member_tag),
                'last_name': last_name,
                'chamber': get_chamber(matched_cong_member_tag),
                'type': get_type(matched_cong_member_tag),
                'party': get_party(matched_cong_member_tag),
                'state': get_state(matched_cong_member_tag),
                'district': None,
                'bio_guide_id': get_bioguide_id(matched_cong_member_tag),
                'congress_id': get_congress_id(matched_cong_member_tag)}

def get_authority_id_from_mods(last_name, mods_file_path):
    matched_cong_member_tag = get_cong_member_tag_from_mods(last_name, mods_file_path)
    if matched_cong_member_tag == None:
        return 99999999999999
    authority_id = get_authority_id(matched_cong_member_tag)
    if authority_id == None:
        return 99999999999999
    else:
        return authority_id

def get_bill_context(bill_tag):
    try:
        return bill_tag.attrs['context']
    except:
        return 'N/A'

def get_bill_congress(bill_tag):
    try:
        return bill_tag.attrs['congress']
    except:
        return 'N/A'

def get_bill_number(bill_tag):
    try:
        return bill_tag.attrs['number']
    except:
        return 'N/A'

def get_bill_type(bill_tag):
    try:
        return bill_tag.attrs['type']
    except:
        return 'N/A'

def populate_speeches(count, folder, next_index):
    
    # speakersDir = Path('/Users/halliday/projects/searchlight/parsing')
    speakers = pd.read_csv('./updatedspeakers.csv')
    
    speeches = pd.DataFrame(columns=["speech_id",
                                 "last_name",
                                 "speaker_id",
                                 "proceeding_id", 
                                 "topic_id", 
                                 "word_count", 
                                 "speech_text",
                                 "file_name",
                                 "mods_file"])
    
    bills = pd.DataFrame(columns=["mods_file",
                              "congress_id",
                              "context",
                              "bill_number",
                              "bill_type"])

    #collects speaker-speech pairs from text files
    def collect_pairs(folder):
        nonlocal speeches
        nonlocal next_index
        speech_count = next_index
        folder_path = "./" + folder
        list_of_files = os.listdir(folder_path)
        for file in list_of_files:
            if file.endswith(".txt"):
                # print(file)
                if file == 'CREC-2018-03-22-pt1-PgH1769-2.txt':
                    continue
                if file == 'CREC-2017-09-06-pt1-PgH6695.txt':
                    continue
                file_path = "./" + folder + "/" + file
                mods_file = file.replace('.txt', '.xml')
                separated = sep_speech(file_path)
                i = 0
                while i < len(separated):
                    separated_surname = fix_surname_typos(separated[i])
                    text = separated[i+1]
                    text = text.replace('MrPresident', 'Mr. President')
                    if len(text) > 30:
                        row = {"speech_id": speech_count,
                               "last_name": separated_surname,
                               "speaker_id": 99999999999999,
                               "proceeding_id": "proceeding_id", 
                               "topic_id": "topic_id",
                               "word_count": len(text.split()), 
                               "speech_text": text,
                               "file_name": file,
                               "mods_file": mods_file}
                        speech_count += 1
                        speeches = speeches.append(row, ignore_index=True)     
                    i += 2
                # print('finished with file ', speech_count)
        print("finished generating speaker-speech pairs, folder: " + folder)
    
    collect_pairs(folder)
        
    def get_speaker_id(last_name, mods_file_path):
        nonlocal speakers
        possible_speakers = speakers[speakers['last_name'] == last_name]
        if possible_speakers.shape[0] == 0:
            new_speaker = get_cong_member_info(last_name, mods_file_path)
            speakers = speakers.append(new_speaker, ignore_index=True)
            print(speakers.shape[0])
            speakers = speakers.sort_values('last_name')
            speakers.to_csv('updatedspeakers.csv', index=False)
            print("wrote in new speaker")
            print(new_speaker)
            return new_speaker['speaker_id']
        elif possible_speakers.shape[0] == 1:
            # print('used existing row')
            return possible_speakers.iloc[0]['speaker_id']
        else:
            mods_speaker_id = get_authority_id_from_mods(last_name, mods_file_path)
            if int(mods_speaker_id) > 100000:
                print("speaker not found in mods: " + last_name)
                return None
            matched_speaker = possible_speakers[possible_speakers['speaker_id'] == int(mods_speaker_id)]
            if matched_speaker.shape[0] == 1:
                # print("speaker matched successfully, used existing row")
                return matched_speaker.iloc[0]['speaker_id']
            elif matched_speaker.shape[0] == 0:
                new_speaker = get_cong_member_info(last_name, mods_file_path)
                speakers = speakers.append(new_speaker, ignore_index=True)
                print("wrote in new speaker")
                print(new_speaker)
                speakers = speakers.sort_values('last_name')
                speakers.to_csv('updatedspeakers.csv', index=False)
                return new_speaker['speaker_id']
    
    def get_bills(mods_file_path, mods_file):
        nonlocal bills
        
        file_exists = bills[bills['mods_file'] == mods_file]
        if file_exists.shape[0] > 0:
            return
        
        try:
            handler = open(mods_file_path).read()
        except:
            return
        soup = Soup(handler, "lxml")
        bill_tags = soup.find_all("bill")

        if len(bill_tags) == 0:
            return
        else:
            for bill_tag in bill_tags:
                new_bill_row = {"mods_file": mods_file,
                               "congress_id": get_bill_congress(bill_tag),
                               "context": get_bill_context(bill_tag),
                               "bill_number": get_bill_number(bill_tag),
                               "bill_type": get_bill_type(bill_tag)}
                bills = bills.append(new_bill_row, ignore_index=True)        
    
    #initialize new columns
    speeches['proceeding_title'], speeches['year'], speeches['month'], speeches['day'] = "", 0, 0, 0
    
    #collect speaker_ids, titles, dates, and bills
    for i in range(speeches.shape[0]):
        
        curr_row = speeches.iloc[i]
        last_name = curr_row['last_name']
        mods_file_path = "./" + folder + "/" + curr_row['mods_file']
        text_file_path = "./" + folder + "/" + curr_row['file_name']
        
        #collect speaker_ids, titles, and dates
        speaker_id = get_speaker_id(last_name, mods_file_path)
        title = find_title(text_file_path)
        year, month, day = sep_date_from_file(curr_row['file_name'])
        
        speeches.loc[i, "speaker_id"] = speaker_id
        speeches.loc[i, "proceeding_title"] = title
        speeches.loc[i, "year"] = int(year)
        speeches.loc[i, "month"] = int(month)
        speeches.loc[i, "day"] = int(day)
        
        #populate bills table if necessary
        get_bills(mods_file_path, curr_row['mods_file'])
    
    speeches = speeches.sort_values('speech_id')
    bills = bills.sort_values('mods_file')
    
    speeches.to_csv('./parsing_results/' + 'speeches_' + str(count) + ".csv", index=False)
    bills.to_csv('./parsing_results/' + 'bills_' + str(count) + ".csv", index=False)
    
    print("                " + "saved " + "speeches_" + str(count))
    print("                " + "saved " + "bills_" + str(count))
    
    return max(speeches['speech_id'])
    
#running parser

count = 1
folders = os.listdir("./scraped_folders")
print(folders)
next_index = 0
for folder in folders:
    print("                " + folder)
    next_index = populate_speeches(count, "scraped_folders/" + folder, next_index)
    next_index += 1
    count += 1


