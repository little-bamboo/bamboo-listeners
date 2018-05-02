from optparse import OptionParser
import os
import sys

import praw
from image_search import image_search_api
import time

import pymongo
import boto3
import json


def main(cmdline=None):
    reddit = praw.Reddit(client_id='Ikg-70xosKhdYQ',
                         client_secret='e92PkMze-4xXKR8reKbdTd0F5H8', password='Schaper7',
                         user_agent='PrawTut', username='seattleracer38')

    subreddit = reddit.subreddit('jokes')

    hot_jokes = subreddit.hot()

    images = image_search_api.image_search_api()
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')

    client = pymongo.MongoClient()
    db = client.reddit_joke_bot

    counter = 0
    for submission in hot_jokes:
        joke_object = {}
        if len(submission.selftext) < 60:
            key_phrases = comprehend.detect_key_phrases(Text=submission.title, LanguageCode='en')

            phrases = key_phrases['KeyPhrases']
            phrase_list = []
            for phrase in phrases:
                phrase_list.append(phrase['Text'].encode('utf-8'))

            phrase_list = ' '.join(phrase_list)

            images_returned = images.search(phrase_list)
            if images_returned:
                joke_image = images_returned[0]
            else:
                joke_image = 'none.png'

            joke_object['title'] = submission.title
            joke_object['punchline'] = submission.selftext
            joke_object['key_phrases'] = key_phrases
            joke_object['image'] = joke_image
            joke_object['created'] = submission.created
            joke_object['author'] = submission.author.name
            joke_object['over_18'] = submission.over_18
            joke_object['permalink'] = submission.permalink
            joke_object['score'] = submission.score
            joke_object['id'] = submission.id
            joke_object['num_comments'] = submission.num_comments

            print(joke_object)
            print('---------------')
            time.sleep(4)

            try:
                db.reddit_jokes.insert_one(joke_object)
            except pymongo.errors.DuplicateKeyError, e:
                print "Duplicate Key Error: {0}".format(e)
            except:
                print "Something else went wrong on the insert"

            counter += 1
            if counter > 100:
                break

    db.reddit_jokes.count()
    return 0


if __name__ == "__main__":
    # this runs when the application is run from the command
    # it grabs sys.argv[1:] which is everything after the program name
    # and passes it to main
    # the return value from main is then used as the argument to
    # sys.exit, which you can test for in the shell.
    # program exit codes are usually 0 for ok, and non-zero for something
    # going wrong.
    sys.exit(main(sys.argv[1:]))
