"""main_info.py

This script contains private functions for scraping the review pages

This script contains the following functions:

    * _get_critic_reviews_from_page - scrapes info per critic page
    * _get_num_pages - finds number of pages to scrape
    * get_critic_reviews - scrapes info over all critic pages 

Required Packages: None
"""


# base
import re
from datetime import datetime

# this package
from .util import _make_soup
from .util import _build_url

#####################
# interal functions #
#####################

def _get_critic_reviews_from_page(soup):
    result = []
    reviews = soup.findAll('div', class_=re.compile('top_critic'))
    if reviews:
        for review in reviews:
            # top critic or not
            critic_top = review.find(lambda x: 'Top Critic' in x.text)
            if critic_top is not None:
                critic_top = critic_top.get_text().strip()
            
            # critic publication
            publication = review.find_next_sibling('div', class_=re.compile('critic_name'))
            if publication is not None:
                publication = publication.find('em', class_=re.compile('critic-publication'))
                if publication is not None:
                    publication = publication.get_text().strip()
            
            # review date
            review_date = review.find_next('div', class_ = re.compile('review-date'))
            if review_date is not None:
                review_date = datetime.strptime(review_date.get_text().strip(), '%B %d, %Y').strftime('%d/%m/%Y')
            
            # critic icon
            critic_icon = review.find_next('div', class_ = re.compile('review_icon'))
            if critic_icon is not None:
                critic_icon = critic_icon['class'][-1].strip()
                
            # critic score
            critic_score = review.find_next('div', class_ = re.compile('review-link'))
            if critic_score is not None:
                critic_score = re.search('Original Score:\s*?([^\s]+?)\s+?', critic_score.get_text())
                if critic_score is not None:
                    critic_score = critic_score.group(1).strip()
            # review content
            review_content = review.find_next('div', class_ = re.compile('the_review'))
            if review_content is not None:
                review_content = review_content.get_text().strip()
            result.append([review_date, publication, critic_icon, critic_top, critic_score, review_content])
    return result

def _get_num_pages(soup):
    """Find the number of pages to scrape reviews from
    :param soup: html soup from BeautifulSoup
    :type soup: bs4 object
    :return: number of pages with reviews
    :rtype: str
    """
    page_pat = re.compile(r'Page 1 of \d+')
    match = re.findall(page_pat,str(list(soup)))
    if len(match) > 0:
        match = match[0]
        match = match.split(' of ')[-1]
        return match
    else:
        return None

##################
# user functions #
##################
    
def get_critic_reviews(page: str, verbose:bool = True):
    """Crawls critic review pages for the given movie.
    Returns a list of lists: 
    movie_link, movie_id, review_date, critic_publication,
    critic_icon, critic_top, critic_score, review_content

    :param page: main page url for movie
    :type page: str, e.g., 'https://www.rottentomatoes.com/m/the_lion_king'
    :return: a list of lists containing reviews
    """

    # containers
    review_info = []
        
    # get movie id
    soup = _make_soup(page)
    if soup == '':
        movieId = None
    else:
        # movie id
        movieId = soup.find('a', href=re.compile('movieId=[0-9]+'))
        if movieId is not None:
            movieId = '/m/'+ re.search('movieId=([0-9]+)$', movieId['href']).group(1)
    
    soup = _make_soup(page + "/reviews")
    
    # get number of pages
    pages = _get_num_pages(soup)
    
    if pages is not None:
        # verbose option
        if verbose:
            print('scraping critic reviews')
            print('scraping url: ' + page + "/reviews " + str(pages) + " pages to scrape")
        
        # extraction
        for page_num in range(1,int(pages)+1):
            soup = _make_soup(page + "/reviews?page=" + str(page_num))
            info_per_page = _get_critic_reviews_from_page(soup)
            print('done scraping for page: {}'.format(page_num))
            # append review infos
            if info_per_page:
                review_info.extend([[page, movieId] + i for i in info_per_page])
        # verbose option
        if verbose:
            print('done scraping critic reviews')
    else:
        # if no pages (i.e., no reviews), return None
        print('No review pages found..')
        review_info = None
        
    return review_info
