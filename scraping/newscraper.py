import requests
from bs4 import BeautifulSoup
import re
import sys
import traceback
import time

def log(message):
    with open("testlogs.txt", "a") as logsfile:
        logsfile.write(message + "\n")

def create_text_file_name(url):
    pattern = '(?<=html/).*'
    name = re.findall(pattern, url)
    return name[0][:-3] + 'txt' 

def extract_mods_from_url(url):
    try:
        stuff = requests.get(url)
    except Exception as e:
        log("         " + "ERROR")
        log("         " + repr(e))
        log("         " + "Failed to complete mods get request from: " + str(url))
        return
    stuff_parsed = BeautifulSoup(stuff.content, 'lxml')
    try:
        return str(stuff_parsed.find('mods'))
    except Exception as e:
        log("         " + "ERROR")
        log("         " + repr(e))
        log("         " + "Could not extract mods at: " + str(url))

def extract_text_from_url(url):
    try:
        stuff = requests.get(url)
    except Exception as e:
        log("         " + "ERROR")
        log("         " + repr(e))
        log("         " + "Failed to complete text get request from: " + str(url))
        return
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
        log("         " + "ERROR")
        log("         " + repr(e))
        log("         " + "Failed to write text into file. file_name: " + str(file_name) + ", url: " + str(url))
    file.close()
    return file_name

def extract_mods(url, text_file_name):
    extracted_mods = extract_mods_from_url(url)
    file_name = text_file_name[0:-3] + 'xml'
    file = open("./scraped_files/" + file_name, 'w')
    # print statements/errors here
    try:
        file.write(extracted_mods)
    except Exception as e:
        log("         " + "ERROR")
        log("         " + repr(e))
        log("         " + "Failed to write mods into file. file_name: " + str(file_name) + ", url: " + str(url))
    file.close()

try:
    root_url = "https://www.gpo.gov"
    page = requests.get('https://www.gpo.gov/fdsys/browse/collection.action?collectionCode=CREC')
    soup = BeautifulSoup(page.content, 'html.parser')
    years = soup.find_all('div', class_='level1')
    years = years[19:]
    for year in years:
        try:
            log(year.text.strip())
            print(year.text.strip())
        except:
            log(str(year))
            print(str(year))
        year_tag = year.find("a")
        year_on_click = year_tag['onclick'][12:-20]
        year_url = root_url + year_on_click
        year_page = requests.get(year_url)
        year_soup = BeautifulSoup(year_page.content, 'html.parser')
        months = year_soup.find_all('div', class_='level2')
        for month in months:
            try:
                log("         " + month.text.strip())
                print("         " + month.text.strip())
            except:
                log("         " + str(month))
                print("         " + str(month))
            month_tag = month.find("a")
            month_on_click = month_tag['onclick'][12:-20]
            month_url = root_url + month_on_click
            month_page = requests.get(month_url)
            month_soup = BeautifulSoup(month_page.content, 'html.parser')
            days = month_soup.find_all('div', class_='level3')
            for day in days:
                day_tag = day.find("a")
                day_on_click = day_tag['onclick'][12:-20]
                day_url = root_url + day_on_click
                day_page = requests.get(day_url)
                day_soup = BeautifulSoup(day_page.content, 'html.parser')
                sections = day_soup.find_all('div', class_='level4 browse-leaf-level ')
                for section in sections:
                    if section.text.strip() == 'House':
                        house_tag = section.find("a")
                        house_on_click = house_tag['onclick'][12:-20]
                        house_url = root_url + house_on_click
                        house_page = requests.get(house_url)
                        house_soup = BeautifulSoup(house_page.content, 'html.parser')
                        download_links = house_soup.find_all('td', class_='browse-download-links')
                        for download_link in download_links:
                            download_link_tags = download_link.find_all("a")
                            for download_link_tag in download_link_tags:
                                if download_link_tag.text == '' and download_link_tag.text != 'PDF' and download_link_tag.text != 'Text':  
                                    more_page = requests.get(root_url + "/fdsys/" + download_link_tag['href'])
                                    more_soup = BeautifulSoup(more_page.content, 'html.parser')
                                    table = more_soup.find('table', class_="page-details-budget-metadata-table")
                                    try:
                                        leaf_links = table.find_all('a')
                                    except Exception as e:
                                        log("         " + "ERROR")
                                        log("         " + repr(e))
                                        log("         " + "Could not retrieve table at: " + str(root_url + "/fdsys/" + download_link_tag['href']))
                                        leaf_links = []
                                    text_file_name = ""
                                    for leaf_link in leaf_links:
                                        if leaf_link.text == 'Text':
                                            text_url = leaf_link['href']
                                            text_file_name = extract_text(text_url)
                                            # print(text_file_name)
                                        if leaf_link.text == 'MODS':
                                            mods_url = leaf_link['href']
                                            extract_mods(mods_url, text_file_name)
except Exception as e:
    print('ERROR CAUGHT: ' + repr(e))
    error_file = open("error_log.txt", "w")
    traceback.print_exc(file=error_file)
    print("Check error_log.txt file for traceback")

