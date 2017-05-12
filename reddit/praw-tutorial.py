import praw
import csv

reddit = praw.Reddit(client_id='Ikg-70xosKhdYQ',
                     client_secret='e92PkMze-4xXKR8reKbdTd0F5H8',
                     password='Schaper7',
                     user_agent='testscript by /u/seattleracer38',
                     username='seattleracer38')

print reddit.user.me()

submission = reddit.submission(id='1czuut')
submission.comment_sort = 'top'
submission.comments.replace_more(limit=100, threshold=0)
print submission.comments
counter = 0


with open('jokes.csv', 'w') as jokefile:
    writer = csv.writer(jokefile, delimiter=',')
    for top_comm in submission.comments:
        counter += 1
        print(top_comm.body)
        writer.writerow([counter, top_comm, top_comm.body.encode('utf-8')])

jokefile.close()