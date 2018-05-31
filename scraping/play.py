import requests
from bs4 import BeautifulSoup
import re
import sys
import traceback

more_page = requests.get("https://www.gpo.gov/fdsys/search/pagedetails.action?collectionCode=CREC&browsePath=2018%2F01%2F01-10%5C%2F4%2FHOUSE&granuleId=CREC-2018-01-10-pt1-PgH132-5&packageId=CREC-2018-01-10&fromBrowse=true")
more_soup = BeautifulSoup(more_page.content, 'html.parser')
table = more_soup.find('table', class_="page-details-budget-metadata-table")

print(table)