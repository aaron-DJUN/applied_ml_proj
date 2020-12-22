"""util.py

This file contains private helper methods that facilitate web interaction.

This file contains the following functions:

    * _make_soup - request webpage and make it readable
    * _is_page_error - check if requested page is a 404 or a internal server error occurs
    * _format_name - convert input movie name to url format
    * _build_url - builds a url for main page if input

Required Packages: BeautifulSoup
"""

# base
import requests
import time

# requirements
from bs4 import BeautifulSoup
from requests import TooManyRedirects

# this package
from .const import RT_BASE_URL, DEFAULT_CRAWL_RATE
    
    
def _make_soup(url: str, crawl_rate: float = DEFAULT_CRAWL_RATE):
    """Request url and get content of page as html soup
    :param url: the url to scrape from rotten tomato
    :param crawl_rate: time in seconds between secessive requests
    :type crawl_rate: float
    :return: html content from bs4 html parser
    :rtype: bs4 object
    """
    if crawl_rate <= 0:
        raise Exception('Argument `crawl_rate` must not be less than \
        or equal to 0. The input value was {}'.format(crawl_rate))
    else:
        time.sleep(crawl_rate)
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
        except TooManyRedirects:
            soup = ''
        return soup

def check_min_delay() -> float:
    """Requests the Rotten Tomatoes robots.txt and checks for crawl-delay

    Parameters
    ----------
    N/A
        
    Returns
    -------
    float
        minimum delay from crawl-delay directive
        0 if no crawl-delay is listed
    """
    
    user_found = False
    min_delay = 0
    
    f = requests.get('https://www.rottentomatoes.com/robots.txt')
    soup = BeautifulSoup(f.content, 'html.parser')
    lines = str(soup).split('\n')
    
    for line in lines:
        if 'User-agent: *' in line:
            user_found = True
        if user_found and ('crawl-delay' in line):
            min_delay = float(line.split(':')[1].strip())
    if user_found:
        print('Warning: crawl-delay not listed for "User-agent: *". \nReturning 0.')
    return min_delay
    
def _is_page_error(soup: str) -> bool:
    """Checks if a 404 page/internal server error is returned
    :param soup: html content from a webpage
    :type soup: str
    :return: True/False        
    """
    
    if 'str' not in str(type(soup)):
        soup = str(soup)
    if '<h1>404 - Not Found</h1>' in soup or '<h1>Internal Server Error</h1>' in soup:
        return True
    else:
        return False
        
def _format_name(m_name: str, sep: str = '_') -> str:
    """Formats name for url
    :param m_name: name of movie
    :type m_name: str
    :param sep: word seperator to use '-' or '_'
    :type sep: str
    :return: movie name formatted for url insertion
    :rtype: str
    """
    
    # enforce lower case
    m_name = m_name.lower()
    
    # remove any punctuation
    remove_items = "'-:,"
    for i in remove_items:
        if i in m_name:
            m_name = m_name.replace(i,'')
    m_name = m_name.strip('"')
    return m_name.replace(' ', sep)
    
def _build_url(m_name: str, m_type: str = 'Movie', sep: str = '_') -> str:
    """Builds url for main page of movie
    :param m_name: the url to scrape from RT
    :type m_name: str
    :param m_type: type, default "Movie"
    :type m_type: str
    :param sep: word seperator to use '-' or '_' typically
    :type str: str
    :return: movie url 
    :rtype: str
    """
    
    if m_type == 'Movie':
        url = RT_BASE_URL + 'm/' + _format_name(m_name, sep) 
    else:
        raise Exception('Argument `m_type` must be `Movie`')
    return url
            
