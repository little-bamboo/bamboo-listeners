import requests
import sys
import getopt

from sqlalchemy import create_engine


def inputs(argv):
    print("Processing command line arguments")
    inputfile = ''
    outputfile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('<example>.py -i <inputfilepath> -o <outputfilepath>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('<example>.py -i <inputfilepath> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputfile = arg
    return [inputfile, outputfile]


def read_articles_table(table):
    print ("reading articles table for comment URL list")
    engine = create_engine('mysql+mysqlconnector://dbBambooDev:B@mboo99@bambooiq.ddns.net:3306/dbBambooDev')
    conn = engine.connect()

    url_list = conn.execute("SELECT commentjsURL FROM bs_articlesList").fetchall()

    print(len(url_list))
    print(url_list[0:25])

    return url_list


def fetch_comment_header(self):
    print("fetching comment header")
    pass


def build_comment_url_list(self):
    print("building comment url list")
    pass


def request_comments_from_urls(self):
    print("request comments from urls")
    pass


def post_comments_to_db(self):
    print("post comments to db")
    pass


if __name__ == "__main__":

    print("sqlalchemy version: " + str(sqlalchemy.__version__))
    app_name = "comment-extract"

    # TODO: Implement argument testing
    print('Number of arguments:', len(sys.argv))
    print('Argument List:', str(sys.argv))

    arguments = inputs(sys.argv[1:])

    if arguments:
        print arguments

    table_name = "bs_articleList"

    comment_url_list = read_articles_table(table_name)

    fetch_comment_header
    build_comment_url_list
    request_comments_from_urls
    post_comments_to_db

