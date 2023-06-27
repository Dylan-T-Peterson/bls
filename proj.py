from subprocess import getoutput
import re
from io import StringIO

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import bs4
import pandas as pd
from numpy import arange


def link_diver(base_url: str,a_tag: bs4.element.Tag) -> bs4.BeautifulSoup:
    """Return contents/page source of child page from href link.

    Keyword arguments:
    url -- base URL for a_tag variable
    a_tag -- a_tag element from page source
    """
    driver.get(
        '{0}{1}'.format(base_url,
                        str(a_tag).split('"')[1])
        )
    content = driver.page_source
    page_source_ = bs4.BeautifulSoup(content, features='html.parser')
    return page_source_


if __name__ == '__main__':
    # Initializes needed parameters, and changes options to Firefox Snap bin.
    REGKEY = open('data/REGKEY').read()
    URL = 'https://download.bls.gov'

    options = Options()
    options.binary_location = getoutput(
        'find /snap/firefox -name firefox'
        ).split('\n')[-1]

    driver = webdriver.Firefox(service =
        Service(executable_path = getoutput(
            'find /snap/firefox -name geckodriver'
            ).split('\n')[-1]),
        options = options)

    # Pulls 2 character series IDs and ID names to ID_names dictionary
    # Does not pull non TimeSeries data (en, ew)
    driver.get('https://www.bls.gov/help/hlpforma.htm')
    SID = bs4.BeautifulSoup(driver.page_source, features='html.parser')

    ID_names = {}
    for series_names in SID.find_all(name='h3'):
        ID_names[series_names['id'].lower()] = series_names.contents[0].strip()



    driver.get('https://download.bls.gov/pub/time.series/')
    content = driver.page_source
    stew = bs4.BeautifulSoup(content, features='html.parser')

    # Series ID format seems to be:
    # {prefix}
    # {seasonal adjust}
    # {category|division}
    # {age|length of service (los)|race|gender|part of body (pob)
    # |event|source|occupation|nature|industry}
    # {data type}
    # {case}

    toremove = []
    for key in ID_names.keys():
        valid_tag = (
            stew.find(name='a', href=re.compile(
            f'/pub/time.series/{key}/'
            )))
        if valid_tag == None:
            toremove.append(key)
            continue
    for removed in toremove:
        del ID_names[removed]

    # Grabs choice var from user, validates it against len of ID_names and
    #converts it to chosen ID name
    choice = 1
    for ID_name in ID_names:
        print(f'{choice}) {ID_names[ID_name]}')
        choice += 1
    choice = input('Which series would you like to create an ID for?: ')

    while type(choice) != int:
        try:
            choice = int(choice)
        except:
            choice = input('Please input a valid number option: ')
            continue
        if choice not in arange(1, (ID_names.__len__()+1)):
            choice = input('Please input a valid choice: ')
    choice = list(ID_names.keys())[choice - 1]
    print(choice)

    driver.get(URL + f'/pub/time.series/{choice}/')
    soup = bs4.BeautifulSoup(driver.page_source, features='html.parser')



        ## Creates a Pandas dataframe from the newly pulled ID code page
    for links in soup.find_all(name='a', href=re.compile(
        '/pub/time.series/../..\.(?!data\.|txt|series|aspect|contacts)'
        )):
        ingredients = link_diver(URL, b)

        for c in ingredients.find_all(name='pre'):
            data = StringIO(c.get_text())
            df = pd.read_csv(filepath_or_buffer=data, sep='\t')
            print(df)
            #pass