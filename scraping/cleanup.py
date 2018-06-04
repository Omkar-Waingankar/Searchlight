import requests
from bs4 import BeautifulSoup
import re
import sys
import traceback
import time

def log(message):
    with open("cleaned_logs.txt", "a") as logsfile:
        logsfile.write(message + "\n")

def create_text_file_name(url):
    pattern = '(?<=html/).*'
    name = re.findall(pattern, url)
    return name[0][:-3] + 'txt' 

def extract_mods_from_url(url):
    stuff = requests.get(url)
    stuff_parsed = BeautifulSoup(stuff.content, 'lxml')
    try:
        return str(stuff_parsed.find_all('mods')[0])
    except:
        log("         " + "ERROR")
        log("         " + "Could not extract mods at: " + str(url))

def extract_text_from_url(url):
    stuff = requests.get(url)
    stuff_parsed = BeautifulSoup(stuff.content, "html.parser")
    return stuff_parsed.get_text()

def extract_text(url):
    extracted_text = extract_text_from_url(url)
    file_name = create_text_file_name(url)
    file = open("./scraped_files/" + file_name,'w')
    # print statements/errors here
    try:
        file.write(extracted_text)
    except Exception as e:
        log("         " + "Failed to write text into file. file_name: " + str(file_name) + ", url: " + str(url))
        error_file = open("error_log.txt", "w")
        traceback.print_exc(file=error_file)
    file.close()
    log("text written")
    return file_name

def extract_mods(url, text_file_name):
    extracted_mods = extract_mods_from_url(url)
    file_name = text_file_name[0:-3] + 'xml'
    file = open("./scraped_files/" + file_name, 'w')
    # print statements/errors here
    try:
        file.write(extracted_mods)
    except Exception as e:
        log("         " + "Failed to write mods into file. file_name: " + str(file_name) + ", url: " + str(url))
        error_file = open("error_log.txt", "w")
        traceback.print_exc(file=error_file)
    file.close()
    log("mods written")

root_url = "https://www.gpo.gov"

try:
    file = open("./testlogs.txt")
    file_content = file.read()
    matches = re.findall("(?<=table at:\s)(.*?)(?=\\n)", file_content)
    for match in matches:
        log(match)
        more_page = requests.get(match)
        more_soup = BeautifulSoup(more_page.content, 'html.parser')
        table = more_soup.find('table', class_="page-details-budget-metadata-table")
        try:
            leaf_links = table.find_all('a')
        except Exception as e:
            log("         " + "ERROR")
            log("         " + repr(e))
            log("         " + "Could not retrieve table at: " + str(match))
            leaf_links = []
        text_file_name = ""
        for leaf_link in leaf_links:
            if leaf_link.text == 'Text':
                text_url = leaf_link['href']
                text_file_name = extract_text(text_url)
            if leaf_link.text == 'MODS':
                mods_url = leaf_link['href']
                extract_mods(mods_url, text_file_name)
except Exception as e:
    log("         " + "Something really bad happened: " + repr(e))
    error_file = open("error_log.txt", "w")
    traceback.print_exc(file=error_file)
