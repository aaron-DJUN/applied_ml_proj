"""scraper.py

This script contains the main scraping functions

This script contains the following functions:

    *  scrape_movie_info - main movie scraper

Required Packages: None
"""
# base
from typing import List, Dict

# this package
from .util import _is_page_error, _build_url, _make_soup
from .main_info import get_movie_info
from .reviews import get_critic_reviews

def scrape_movie_info(movie_name: str, verbose:bool = True) -> [Dict[str,str], List[list]]:
    """Get the main info and critic reviews for input movie.
    :param movie_name: movie name to be scraped, e.g., 'The Lion King'
    :type movie_name: str
    :return:(
        dict containing main information about the movie,
        dict containing the review information
        )
    :rtype: a tuple - (dict, list)
    """
    
    unable_to_scrape = True
    
    # determine if url can be used
    seps = ['_', '-']
    for _ in seps:
        movie_url = _build_url(movie_name)
        soup = _make_soup(movie_url)
        is_err = _is_page_error(soup)
        if not is_err:
            unable_to_scrape = False
            break
    
    # scrape page if possible
    if not unable_to_scrape:
        # verbose option
        if verbose:
            print('found ' + movie_name)
            
        main_info = get_movie_info(movie_url, verbose)
        critic_reviews = get_critic_reviews(movie_url, verbose)
        
        return main_info, critic_reviews
    else:
        print('unable to scrape ' + movie_name)
        return None, None