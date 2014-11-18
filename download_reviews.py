"""
Downloads all reviews for the Shawshank Redemption movie from IMDB
Review:
- Text
- Author
- (x,y) tuple that is: x/y people found this review useful

"""

from urllib import urlopen
from bs4 import BeautifulSoup
import pickle

OUTFILE = 'shaw_revs.pkl'


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
    authors = [sub.find_all("a")[1].getText() for sub in subdivs]
    xys = [process_x_outof_y(sub.find("small").getText()) for sub in subdivs]
    # making into list of dicts
    out = []
    for author, text, stat in zip(authors, review_texts, xys):
        out.append({'author': author, 'text': text, 'stat': stat})
    return out

    #return {'author': author, 'text': text, 'stat': stat for (author, text, stat) in zip(authors, review_texts, xys)}


URL = 'http://www.imdb.com/title/tt0111161/reviews?start=%s'
page = 0
all_reviews = []
while True:
    html = urlopen(URL%page).read()
    reviews = process_html(html)
    if not reviews:
        break  # no more reviews left
    all_reviews.extend(reviews)
    page += 10

    if page % 100 == 0:
        print len(all_reviews)


#pickling the list of reviews:
with open(OUTFILE, 'wb') as f:
    pickle.dump(all_reviews, f)

# ------------------------------------------------- writing to csv -----------------------------------
# saving to csv:
# print 'writing to csv:'
# cols = ['author', 'text', 'stat']
# with open(OUTFILE, 'wb') as f:
#     dict_writer = csv.DictWriter(f, cols)
#     dict_writer.writer.writerow(cols)
#     dict_writer.writerows(all_reviews)



