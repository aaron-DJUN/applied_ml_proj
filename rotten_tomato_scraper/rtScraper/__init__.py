# author: ZHANG AOJUN
"""__init__.py

Initializes module.

This file requires that `BeautifulSoup` be installed within the Python
environment you are running in.

"""

#====================
# Primary User Access
#====================

from .scraper import scrape_movie_info
from .wikipedia import scrape_movie_names

#=========================
# Supplemental User Access
#=========================

from .reviews import get_critic_reviews
from .main_info import get_movie_info