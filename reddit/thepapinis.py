import praw
import csv
import time
from datetime import datetime, timedelta

reddit = praw.Reddit(client_id='Ikg-70xosKhdYQ',
                     client_secret='e92PkMze-4xXKR8reKbdTd0F5H8',
                     password='Schaper7',
                     user_agent='testscript by /u/seattleracer38',
                     username='seattleracer38')

print reddit.user.me()

subreddit = reddit.subreddit("thepapinis")

date_string = datetime.now().strftime("%Y%m%d")
filename = 'pappini_' + date_string + '.csv'

with open(filename, 'w') as pappinifile:
    writer = csv.writer(pappinifile, delimiter=',', quotechar='"')
    writer.writerow(
        ["row",
         "id",
         "author",
         "url",
         "permalink",
         "created",
         "body",
         "score",
         "approved_by",
         "flair_text",
         "banned_by",
         "controversiality",
         "distinguished",
         "edited",
         "gilded",
         "likes",
         "mod_note",
         "stickied",
         "downs",
         "ups",
         "submission_title",
         "submission_comment_count",
         "submission_preview"
         ])

    counter = 0

    epoch_now = time.time()
    two_years_ago = datetime.now() - timedelta(days=365*2)
    two_years = float(two_years_ago.strftime('%s'))

    for submission in subreddit.submissions(two_years, epoch_now):
        submission.comments.replace_more(limit=100)

        comment_count = 0
        if submission.num_comments:
            comment_count = submission.num_comments

        url = ""
        if submission.url:
            url = submission.url

        submission_title = ""
        if submission.title:
            submission_title = submission.title.encode('utf-8')

        try:
            preview_image = submission.preview["images"][0]["source"]["url"]
        except Exception, err:
            print("Exception: {0}".format(err))
            preview_image = ""

        for top_level_comment in submission.comments.list():

            created_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(top_level_comment.created))
            score = top_level_comment.score

            approved_by = ""
            flair_text = ""
            banned_by = ""
            controversiality = 0
            distinguished = ""
            edited = False
            gilded = 0
            likes = ""
            mod_note = ""
            stickied = False
            downs = 0
            ups = 0

            try:

                if top_level_comment.approved_by:
                    approved_by = top_level_comment.approve

                if top_level_comment.author_flair_text:
                    flair_text = top_level_comment.author_flair_text

                if top_level_comment.banned_by:
                    banned_by = top_level_comment.banned_by

                if top_level_comment.controversiality:
                    controversiality = top_level_comment.controversiality

                if top_level_comment.distinguished:
                    distinguished = top_level_comment.distinguished

                if top_level_comment.edited:
                    edited = top_level_comment.edited

                if top_level_comment.gilded:
                    gilded = top_level_comment.gilded

                if top_level_comment.likes:
                    likes = top_level_comment.likes

                if top_level_comment.mod_note:
                    mod_note = top_level_comment.mod_note

                if top_level_comment.stickied:
                    stickied = top_level_comment.stickied

                if top_level_comment.downs:
                    downs = top_level_comment.downs

                if top_level_comment.ups:
                    ups = top_level_comment.ups

            except Exception, err:
                print"Err: {0}".format(err)

            counter += 1
            print("{0} {1} {2}".format(counter, created_date, top_level_comment.body.encode('utf-8')))
            writer.writerow([counter,
                             top_level_comment.id,
                             top_level_comment.author,
                             url,
                             top_level_comment.permalink,
                             created_date,
                             top_level_comment.body.encode('utf-8'),
                             score,
                             approved_by,
                             flair_text,
                             banned_by,
                             controversiality,
                             distinguished,
                             edited,
                             gilded,
                             likes,
                             mod_note,
                             stickied,
                             downs,
                             ups,
                             submission_title,
                             comment_count,
                             preview_image
                             ])

pappinifile.close()
