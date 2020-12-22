"""main_info.py

This file contains private functions for scraping the main pages .e.g.
`RT_BASE_URL + m/ + MOVIE_NAME`

This file contains the following functions:
    * get_movie_info - scrapes info from a movie main page

Required Packages: None
"""

# base
import re

# this package
from .util import _make_soup
from .util import _build_url


#================#
# user functions #
#================#

def get_movie_info(page: str, verbose:bool = True):
    """Scrapes info from a movie main page

    :param page: the url to scrape from RT
    :type page: str, e.g., 'https://www.rottentomatoes.com/m/the_lion_king'
    :return: dict of scraped info with keys:
        synopsis, rating, genre, studio, director, writer, currency,
        box_office, runtime
    :rtype: dict
    """

    def add_scoreInfo(pattern, raw_text, keyName):
        """inner helper function to help add score information
        :param pattern: pattern to match
        :param raw_text: html text
        :param keyName: key name to be append to the dict
        """
        match_pat = re.search(pattern, raw_text)
        if match_pat is None:
            info[keyName] = None
        else:
            info[keyName] = match_pat.group(1)

    info = dict()   
    
    # verbose option
    if verbose:
        print('scraping main page')
        print('scraping url: ' + page)
        
    # make soup
    soup = _make_soup(page)
    
    if soup == '':
        return None
        
    else:
        ### extraction ###
        # movie id
        movieId = soup.find('a', href=re.compile('movieId=[0-9]+'))
        if movieId is None:
            info['movie_link'] = None
        else:
            movieId = re.search('movieId=([0-9]+)$', movieId["href"])
            info['movie_link'] = '/m/'+ movieId.group(1)
        
        movieInfo= soup.find('script', type="application/ld+json")
        if movieInfo is None:
            print('No movie information for this movie.')
        else:
            # movie name
            movieName = re.search('"name":"?(.+?)"?,"', movieInfo.get_text())
            if movieName is None:
                info['movie_name'] = None
            else:
                info['movie_name'] = movieName.group(1)
            
            # rating
            rating = re.search('"contentRating":"?(.+?)"?,"',movieInfo.get_text())
            if rating is None:
                info['rating'] =  None
            else:
                info['rating'] = rating.group(1)
            
            # genre 
            genre = re.search('"genre":\["(.+?)"\]', movieInfo.get_text())
            if genre is None:
                info['genre'] = None
            else:
                info['genre'] = genre.group(1).replace('"','')
            
            # directors
            directors = re.search('"director":(.+?),"author"', movieInfo.get_text())
            if directors is None:
                info['directors'] = None
            else:
                info['directors'] =  ','.join(re.findall('"name":"(.+?)","', directors.group(1)))
            
            # writers
            writers = re.search('"director":.+?"author":(.+?),"genre"', movieInfo.get_text())
            if writers is None:
                info['writers'] = None
            else:
                info['writers'] = ','.join(re.findall('"name":"(.+?)","', writers.group(1)))
        
        # movie synopsis
        movieSyno = soup.find('div', id=re.compile('movieSynopsis'))
        if movieSyno is None:
            info['movie_info'] = None
        else:
            info['movie_info'] = movieSyno.get_text().strip()
        
        # poster_image
        poster_img = soup.find('meta', property = re.compile('image$'))
        if poster_img is None:
            info['poster_image'] = None
        else:
            info['poster_image'] = poster_img["content"]
        
        # cast
        casts = soup.find_all('div', class_=re.compile('^cast-item'))
        if casts is None:
            info['casts'] = None
        else:
            info['casts'] = ','.join([cast.find('span').get_text().strip() for cast in casts])
        
        # in_theaters_date
        in_theaters_date = soup.find('div', text=re.compile("In Theaters"))
        if in_theaters_date is None:
            info['in_theaters_date'] = None
        else:
            info['in_theaters_date'] = in_theaters_date.find_next_sibling('div').find('time').get_text().strip()
        
        # on_streaming_date
        on_streaming_date = soup.find('div', text=re.compile("On Disc/Streaming:"))
        if on_streaming_date is None:
            info['on_streaming_date'] = None
        else:
            info['on_streaming_date'] = on_streaming_date.find_next_sibling('div').find('time').get_text().strip()
        
        # runtime_in_minutes
        runtime_in_minutes = soup.find('div', text=re.compile("Runtime:"))
        if runtime_in_minutes is None:
            info['runtime_in_minutes'] = None
        else:
            info['runtime_in_minutes'] = re.search('[0-9]+',runtime_in_minutes.find_next_sibling('div').find('time').get_text().strip()).group(0)
        # studio_name
        studio_name = soup.find('div', text=re.compile("Studio:"))
        if studio_name is None:
            info['studio_name'] = None
        else:
            info['studio_name'] = studio_name.find_next_sibling('div', class_="meta-value").get_text().strip()
        
        # Extra: box office
        box_office = soup.find('div', text=re.compile("Box Office:"))
        if box_office is None:
            info['box_office'] = None
        else:
            info['box_office'] = box_office.find_next_sibling('div', class_="meta-value").get_text().strip()
        
        scoreInfo = soup.find('script', type="text/javascript")
        if scoreInfo is None:
            print('No score information for this movie.')
        else:
            pat_head1 = 'root.RottenTomatoes.context.scoreInfo.+?'
            pat_keywrd = '"consensus":'
            pat_tail1 = '"?(.+?)"?,"'
            pat_tail2 = '"?([0-9]+?)"?,"'
            pat_tail3 = '"?([0-9\.]+?)"?,"'
            # critics_consensus
            criticsCns_pat = pat_head1 + pat_keywrd + pat_tail1
            add_scoreInfo(criticsCns_pat, scoreInfo.get_text(), 'critics_consensus')
            
            # tomatometer_status
            pat_keywrd ='"tomatometerState":'
            tmtStatus_pat = pat_head1 + pat_keywrd + pat_tail1
            add_scoreInfo(tmtStatus_pat, scoreInfo.get_text(), 'tomatometer_status')

            # tomatometer_rating
            pat_keywrd = '"score":'
            tmtRating_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(tmtRating_pat, scoreInfo.get_text(), 'tomatometer_rating')

            # tomatometer_count
            pat_keywrd ='"numberOfReviews":'
            tmtCnt_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(tmtCnt_pat, scoreInfo.get_text(), 'tomatometer_count')
            
            # audience_status
            audStatus_pat = 'root.RottenTomatoes.context.popcornMeterState.+?"(.+?)";'
            add_scoreInfo(audStatus_pat, scoreInfo.get_text(), 'audience_status')

            # Extra: audience_want_to_see
            audWantToSee_pat = 'root.RottenTomatoes.context.wantToSeeData.+?"wantToSeeCount":' + pat_tail2
            add_scoreInfo(audWantToSee_pat, scoreInfo.get_text(), 'audience_want_to_see_count')
            
            # audience_rating
            pat_keywrd = '"audienceAll".+?"score":'
            audRating_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audRating_pat, scoreInfo.get_text(), 'audience_rating')

            # audience_count
            pat_keywrd = '"audienceAll".+?"ratingCount":'
            audCnt_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audCnt_pat, scoreInfo.get_text(), 'audience_count')

            # audience_top_critics_count
            pat_keywrd = '"tomatometerTopCritics".+?"numberOfReviews":'
            audTopCritics_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audTopCritics_pat, scoreInfo.get_text(), 'audience_top_critics_count')
            
            # audience_fresh_critics_count
            pat_keywrd = '"freshCount":'
            audFreshCritics_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audFreshCritics_pat, scoreInfo.get_text(), 'audience_fresh_critics_count')
            
            # audience_rotten_critics_count
            pat_keywrd = '"rottenCount":'
            audRottenCritics_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audRottenCritics_pat, scoreInfo.get_text(), 'audience_rotten_critics_count')

            # Extra: audience_fresh_top_critics_count
            pat_keywrd = '"tomatometerTopCritics".+?"freshCount":'
            audFreshCritics_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audFreshCritics_pat, scoreInfo.get_text(), 'audience_fresh_top_critics_count')

            # Extra: audience_rotten_top_critics_count
            pat_keywrd = '"tomatometerTopCritics".+?"rottenCount":'
            audRottenCritics_pat = pat_head1 + pat_keywrd + pat_tail2
            add_scoreInfo(audRottenCritics_pat, scoreInfo.get_text(), 'audience_rotten_rotten_critics_count')
            
            # Extra: tomatometer_avg_rating
            pat_keywrd = '"avgScore":'
            tmtAvgRating_pat = pat_head1 + pat_keywrd + pat_tail3
            add_scoreInfo(tmtAvgRating_pat, scoreInfo.get_text(), 'tomatometer_avg_rating')

            # Extra: audience_top_critics_avg_rating
            pat_keywrd = '"tomatometerTopCritics".+?"avgScore":'
            audTopCriticsAvgRating_pat = pat_head1 + pat_keywrd + pat_tail3
            add_scoreInfo(audTopCriticsAvgRating_pat, scoreInfo.get_text(), 'audience_top_critics_avg_rating')

            # Extra: Score Sentiment
            pat_keywrd = '"scoreSentiment":'
            scoreSentiment_pat = pat_head1 + pat_keywrd + pat_tail1
            add_scoreInfo(scoreSentiment_pat, scoreInfo.get_text(), 'score_sentiment')

            # Extra: audience_avg_rating
            pat_keywrd = '"averageRating":'
            audienceAvgRating_pat = pat_head1 + pat_keywrd + pat_tail3
            add_scoreInfo(audienceAvgRating_pat, scoreInfo.get_text(), 'audience_avg_rating')
            print('done scraping movie info')
        return info