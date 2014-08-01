#!/usr/bin/python3
#code base stolen from /u/GoldenSights
import praw
import time
import sqlite3
import re
import sys

'''USER CONFIGURATION'''

USERNAME = "xxxx"
#This is the bot's Username. In order to send mail, he must have some amount of Karma.
PASSWORD = "xxxx"
#This is the bot's Password.
USERAGENT = "UpdateWeeklyLinks v1.0 /u/boib"
#This is a short description of what the bot does. For example "/u/GoldenSights' Newsletter Bot".
SUBREDDIT = "boibtest"
#This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
MAXPOSTS = 30
#This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
WAIT = 60*30 # just run twice an hour
#This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
'''All done!'''



WAITS = str(WAIT)
sql = sqlite3.connect('UpdateWeeklyLinks.db')
print('Loaded SQL Database')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')
print('Loaded Oldposts')
sql.commit()


r = praw.Reddit(USERAGENT)
r.config.decode_html_entities = True


Trying = True
while Trying:
    try:
        r.login(USERNAME, PASSWORD)
        print('Successfully logged in\n')
        Trying = False
    except praw.errors.InvalidUserPass:
        print('Wrong Username or Password')
        quit()
    except Exception as e:
        print("%s" % e)
        time.sleep(5)

def scan():
    print('Scanning ' + SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_new(limit=MAXPOSTS)
    for post in posts:
        weeklyRecThread     = False
        weeklyReadingThread = False
        pid                 = post.id
        try:
            pauthor = post.author.name
        except AttributeError:
            pauthor = '[deleted]'

        if pauthor == "AutoModerator":
            print (pauthor + " " + post.title)
            if "Weekly Recommendation Thread for the week of" in post.title:
                weeklyRecThread = True
                searchx = "\*\*\[Weekly Recommendation Thread,\]\((http://www.reddit.com/r/books/.*?)\)\*\*"

            elif "What books are you reading this week?" in post.title:
                weeklyReadingThread = True
                searchx = "\*\*\[Weekly \"What Are You Reading\?\" Thread!\]\((http://www.reddit.com/r/books/.*?)\)\*\*"

            if weeklyRecThread or weeklyReadingThread:
                cur.execute('SELECT * FROM oldposts WHERE id=?', [pid])
                if not cur.fetchone():
                    cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
                    sql.commit()

                    #
                    # i have a automod post that's not in my db
                    # 1) get subreddit settings (sidebar)
                    # 2) get weekly rec url from automod's post
                    # 3) replace old url in sidebar with new url
                    # 4) save settings
                    # 5) set flag to not run again until midnight
                    #

                    sr = r.get_subreddit(SUBREDDIT)
                    sb = sr.get_settings()["description"]

                    print ("searchx: " + searchx)
                    matchObj = re.search(searchx, sb)

                    if matchObj:
                       print ("Old url : ", matchObj.group(1))
                       print ("New url : ", post.url)

                       new_sb = sb.replace(matchObj.group(1), post.url)
                       sr.update_settings(description = new_sb)
                       quit() # update one string and quit

                    else:
                       print ("No match!!")
                else:
                    print("Already in db - no action")
while True:
    try:
        scan()
    except Exception as e:
        print('An error has occured:', e)
    print('Running again in ' + WAITS + ' seconds.\n')
    time.sleep(WAIT)


