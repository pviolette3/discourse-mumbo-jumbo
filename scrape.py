from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin

from redis import Redis
import json
import re
import sys
import time

def top_movie_ids():
    resp = requests.get('http://www.imdb.com/chart/top')
    soup = BeautifulSoup(resp.text)
    for link in soup.find_all('a'):
        href = link.attrs['href'] if 'href' in link.attrs else ''
        if href.startswith('/title') and not 'vote' in href:
            url_pattern = re.compile('\/title\/(?P<m_id>\w+)\/\?.*')
            yield url_pattern.search(href).group('m_id')
             
def build_review_url(movie_id):
    return 'http://www.imdb.com/title/{_id}/reviews'.format(_id=movie_id)

def join_key(movie_id, els):
    return 'crawl:{}:{}'.format(movie_id, els)

def crawl(movie_id, redis_con):
    movie_review_url = build_review_url(movie_id)
    html = requests.get(movie_review_url).text
    soup = BeautifulSoup(html)
    main_content = soup.find('div', id='tn15content')
    num_reviews_td = main_content.find('td', text=re.compile('reviews in total'))
    pat = re.compile('(?P<number>\d+)')
    total_reviews = int(pat.search(num_reviews_td.text).group('number'))
    redis_con.set(join_key(movie_id, 'total'), total_reviews)

from html_downloader import download
def dl(args):
    movie_id, start = args
    return (download(movie_id, start), movie_id, start)

def main():
    r = Redis(host='localhost', db=1)
    movie_ids = re.compile('crawl:(?P<m_id>\w+):*')
    top_movie_ids = [movie_ids.search(k).group('m_id') for k in r.keys('crawl:*')]

    p = Pool(5)
    for m_id in top_movie_ids:
        finished_key = 'crawl:{}:finished'.format(m_id)
        total_key = 'crawl:{}:total'.format(m_id)
        started_key = 'crawl:{}:started'.format(m_id)
        next_key = 'crawl:{}:next'.format(m_id)

        finished = bool(r.get(finished_key)) or False
        total = int(r.get(total_key))
        started = r.get(started_key) or False
        next_pages = [10 * i for i in range(0, total // 10 + 1)[:5]]

        if not started:
            r.set(started_key, True)
            r.set(next_key, json.dumps(next_pages))
        else:
            next_pages = json.loads(r.get(next_key))

        while not finished:
            successes = p.map(dl, [(m_id, page) for page in next_pages])
            top = max(next_pages) // 10
            for (success, movie_id, start_page) in successes:
                if success:
                    next_pages.remove(start_page)
              
            if len(next_pages) < 5 and top < total // 10:
                total_to_add = 5 - len(next_pages)
                for page in range(top + 1, total // 10 + 1)[:total_to_add]:
                    next_pages.append(page * 10)

            print m_id, next_pages
            r.set(next_key, json.dumps(next_pages))
            if not next_pages:
                r.set(finished_key, True)
                finished = True
                continue
        time.sleep(1.0)


if __name__ == '__main__':
    main()
