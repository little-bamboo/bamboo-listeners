#!/usr/bin/env python
# encoding: utf-8

from pattern.web import Newsfeed, plaintext
from pattern.db import date
from pattern.vector import Model, Document, LEMMA

news, url = {}, 'http://www.seattletimes.com/feed/'

for story in Newsfeed().search(url, cached=False):
    d = str(date(story.date, format='%Y-%m-%d'))
    s = plaintext(story.description)
    # Each key in the news dict is a date: news is grouped by day
    # Each value is a dictionary of id => story items
    news.setdefault(d, {})[hash(s)] = s

m = Model()
for date, stories in news.items():
    s = stories.values()
    s = ' '.join(s).lower()
    # Each day of news is a single document.
    # By adding all documents to a model we can calculate tf-idf.
    m.append(Document(s, stemmer=LEMMA, exclude=['news', 'day'], name=date))

for document in m:
    print document.name
    print document.keywords(top=10)
