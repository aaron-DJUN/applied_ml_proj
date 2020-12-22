#!/usr/bin/env python3

import rtScraper
import pandas as pd
import time
import argparse
from tqdm import tqdm
if __name__ == '__main__':
    SLACK_TIME = 1
    parser = argparse.ArgumentParser(description='Rotten Tomato Web Scraper', 
                                     usage ='usage: main.py [-h] from_year [--to_year TO_YEAR]')
    parser.add_argument("from_year", type=int, help="from which year to scrape (required)")
    parser.add_argument("--to_year",  type=int, help="to which year to scrape")
    args = parser.parse_args()
    from_year = args.from_year
    to_year = args.to_year if args.to_year is not None else args.from_year
    period = str(from_year) + '_' + str(to_year) if args.to_year is not None else str(from_year)
    start = time.time()
    movie_cnt = tot_cnt = 0
    infos, reviews = [], []
    for year in range(from_year, to_year+1):
        movies = rtScraper.scrape_movie_names(year)
        print('{} movies found for year {}'.format(len(movies), year))
        tot_cnt += len(movies)
        for movie in tqdm(movies):
            movie_info, movie_reviews = rtScraper.scrape_movie_info(movie)
            time.sleep(SLACK_TIME)
            if movie_info is not None:
                movie_cnt +=1
                infos.append(movie_info)
            if movie_reviews is not None:
                reviews.extend(movie_reviews)
    # output
    if infos:
        pd.DataFrame(infos, columns = infos[0].keys()).to_csv('rotten_tomato_movie_info_{}.csv'.format(period))
    if reviews:
        pd.DataFrame(reviews, columns=['movie_link', 'movie_id', 'review_date', 
                                   'critic_publication', 'critic_icon', 'critic_top', 
                                   'critic_score', 'review_content'])\
                                       .to_csv('rotten_tomato_critics_review_{}.csv'.format(period))
    
    print('*' * 80)
    print('Summary:')
    print('{}/{} movies scraped'.format(movie_cnt, tot_cnt))
    print('Time Elapses: {} mins'.format(round((time.time() - start)/60, 3)))
