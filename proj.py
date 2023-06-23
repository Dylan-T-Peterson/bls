from subprocess import getoutput
import re
from io import StringIO

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import bs4
import pandas as pd


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

    # Recursively dives into HTML anchor tag's links till we reach the bottom
    # most level with series ID codes
    for a in stew.find_all(name='a', href=re.compile(
        '/pub/time.series/../'
        )):
        soup = link_diver(URL, a)
        print(a.prettify())

        # Creates a Pandas dataframe from the newly pulled ID code page
        for b in soup.find_all(name='a', href=re.compile(
            '/pub/time.series/../..\.(?!data\.|txt|series|aspect|contacts)'
            )):
            ingredients = link_diver(URL, b)

            for c in ingredients.find_all(name='pre'):
                data = StringIO(c.get_text())
                df = pd.read_csv(filepath_or_buffer=data, sep='\t')
                print(df)