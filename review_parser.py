from bs4 import BeautifulSoup

class  Movie(object):
    def __init__(self, movie_id, name, total_reviews):
        self.movie_id = movie_id
        self.name = name
        self.total_reviews = total_reviews
        
class Author(object):
    def __init__(self, review_id, author_id):
        self.review_id = review_id
        self.author_id = author_id

class Review(object):
    def __init__(self, movie_id, title, text, \
            date, stars, review_number,
            author_id,\
            total_useful, total_feedback):
        super(Review, self).__init__()
        self.movie_id = movie_id
        self.title = title
        self.text = text
        self.date = date
        self.stars = stars
        self.author_id = author_id
        self.review_number = review_number
        self.total_useful = total_useful
        self.total_feedback = total_feedback

import re
def process_html(html):

    def process_x_outof_y(text):
        text = text.split()
        try:
            return (int(text[0]), int(text[3]))
        except:
            return (0,0)

    soup = BeautifulSoup(html)

    # finding the div that contains all of the reviews:
    div = soup.find("div", {"id": "tn15content"})
    subdivs = div.find_all("div")[0::2]

    review_texts = [sub.getText() for sub in div.find_all("p") if sub.getText()
                                            != '*** This review may contain spoilers ***'][:-1]
    review_texts = [review for review in review_texts]
    authors_links = [sub.find_all("a")[1] for sub in subdivs]
    authors = [link.getText() for link in authors_links]
    user_id_re = re.compile('/(?P<_id>\w+)/$')
    author_ids = [user_id_re.search(link.attrs['href']).group('_id') for link in authors_links]
    xys = [process_x_outof_y(sub.find("small").getText()) for sub in subdivs]
    positive_feedbacks = [x[0] for x in xys]
    total_feedbacks = [x[1] for x in xys]

    titles_texts = [sub.find("h2").getText() for sub in subdivs]
    stars_frac = [sub.find("img", width='102').attrs['alt'] for sub in subdivs if sub.find("img", width='102')]
    stars_re = re.compile('(?P<stars>\d+)\/\d+')
    stars = [stars_re.search(frac).group('stars') for frac in stars_frac]

    date_raw_text = [sub.find_all('small')[-1].getText() for sub in subdivs]

    # making into list of dicts
    out = []
    for author, a_id, text, title, stat, star, date, positive_feedback, total_feedback in \
        zip(authors, author_ids, review_texts, titles_texts, xys, stars, date_raw_text, positive_feedbacks, total_feedbacks):
        out.append({
            'author': author,
            'text': text,
            'positive_feedback' : positive_feedback,
            'total_feedback' : total_feedback,
            'ratio' : float(positive_feedback) / float(total_feedback) if total_feedback != 0 else 0,
            'stars' : star,
            'title' : title,
            'author_id' : a_id,
            'date' : date
        })
    return out


from pymongo import MongoClient
import json

def main():
    db = MongoClient().imdb_reviews
    total_reviews = []
    seen = set([])
    movie_id = 'tt0111161' #shawshank redemption
    for reviews in db.raw_reviews.find({'m_id' : movie_id}): 
        if (movie_id, reviews['start']) in seen:
            print 'dup', (movie_id, reviews['start'])
            continue
        seen.add((movie_id, reviews['start']))
        parsed_reviews = process_html(reviews['raw'])
        start = int(reviews['start'])
        for i, review in enumerate(parsed_reviews):
            review['offest'] = start + i
            review['m_id'] = movie_id
        if len(parsed_reviews) != 10:
            print 'not 10 parsed reviews!', len(parsed_reviews), reviews['start']
        total_reviews.extend(parsed_reviews)

    for review in total_reviews:
        db.reviews.insert(review)

    


if __name__ == '__main__':
    main()