import os
import sys

# Path for spark source folder
os.environ['SPARK_HOME']="/usr/local/spark"

# Append pyspark  to Python Path
sys.path.append("your_pyspark_folder ")

try:
    from pyspark import SparkContext
    from pyspark import SparkConf

   print ("Successfully imported Spark Modules")

except ImportError as e:
    print ("Can not import Spark Modules", e)
    sys.exit(1)


# TODO: Import spark context
# TODO: Setup main execution loop

import json
import pandas as pd
from pprint import pprint
import re

def __main__():
    searchresult_clinton = "hdfs:///scrapy/data/clinton-seattletimes-2008-01-01.json"

    clintonResponse = sc.textFile(searchresult_clinton)

    clinton_df = sqlContext.read.json(searchresult_clinton)
    clinton_df_dropped = clinton_df.drop('_corrupt_record')
    clinton_data = clinton_df_dropped.rdd



%pyspark

def cleanString(dirtyString):
    cleanedString = re.sub('[^a-zA-Z0-9 \n\.]', '', dirtyString).replace(".", " ")
    return cleanedString


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)

    return cleanString(cleantext)


def func(data):
    returnDict = {}
    if data[0] is not None:
        returnDict['articleId'] = data[0]
    else:
        returnDict['articleId'] = ""

    if data[1] is not None:
        returnDict['author'] = data[1]
    else:
        returnDict['author'] = ""

    if data[2] is not None:
        returnDict['affiliateAuthor'] = data[2]
    else:
        returnDict['affiliateAuthor'] = ""

    if data[3] is not None:
        returnDict['article'] = data[3]
    else:
        returnDict['article'] = ""

    if data[4] is not None:
        returnDict['category'] = data[4]
    else:
        returnDict['category'] = ""
        # data[5] = comData
    if data[5] is not None:
        commentList = ""
        likeList = []
        collectionIdList = []
        for comData in data[5]:

            if comData.collectionId is not None:
                returnDict['collectionId'] = comData.collectionId
            else:
                returnDict['collectionId'] = 0

            if comData.content.bodyHtml is not None:
                commentList = commentList + cleanhtml(comData.content.bodyHtml.replace(',',' ').replace('.',' ').replace('-',' ').lower())
            else:
                returnDict['comWords'] = ""

        returnDict['likedBy'] = likeList
        returnDict['comWords'] = commentList.split(' ')

    else:
        return ""

    if data[6] is not None:
        returnDict['date'] = data[6]
    else:
        returnDict['date'] = ""

    return [returnDict]


clinton_flat = clinton_data.flatMap(func)
print clinton_flat.take(1)

def filterFunc(data):
    wordList = []
    if data['comWords'] is not None:
        for item in data['comWords']:
            wordList = wordList + [(item, 1)]

    data['comWords'] = wordList
    return data


word_counts_list = clinton_flat.map(filterFunc)

wordcounts = sc.textFile('hdfs://ubuntu1:54310/user/dev/gutenberg') \
        .map( lambda x: x.replace(',',' ').replace('.',' ').replace('-',' ').lower()) \
        .flatMap(lambda x: x.split()) \
        .map(lambda x: (x, 1)) \
        .reduceByKey(lambda x,y:x+y) \
        .map(lambda x:(x[1],x[0])) \
        .sortByKey(False)
wordcounts.take(10)
[(500662, u'the'), (331864, u'and'), (289323, u'of'), (196741, u'to'),
 (149380, u'a'), (132609, u'in'), (100711, u'that'), (92052, u'i'),
 (77469, u'he'), (72301, u'for')]


comment_counts = clinton_flat.map(filterFunc)
print comment_counts.take(1)


def filterFunc(data):
    wordDict = {}
    for key, value in data['comData'].iteritems():
        value = (value, 1)

    data['wordDict'] = wordDict
    return data


comment_counts = clinton_flat.map(filterFunc)
print comment_counts.take(10)

% pyspark


def reduceFunc(data):
    wordList = []
    if data["comWords"] is not None:
        for item in data["comWords"]:
            wordList = wordList + [(item)]

    data['comWords'] = wordList.split()
    return data

reduced_comment_count = comment_counts.reduceByKey(reduceFunc)