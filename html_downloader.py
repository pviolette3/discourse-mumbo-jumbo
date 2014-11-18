from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests

def build_url(movie_id, start):
    return 'http://www.imdb.com/title/{m_id}/reviews?start={start}'.format(m_id=movie_id, start=start)

def download(movie_id, start):
    print 'downloading', movie_id, start
    resp = requests.get(build_url(movie_id, start))
    if not resp.ok:
        return False
    html = resp.text
    db = MongoClient().imdb_reviews
    db.raw_reviews.insert({
        'm_id' : movie_id,
        'start' : start,
        'raw' : html
    })
    return True
