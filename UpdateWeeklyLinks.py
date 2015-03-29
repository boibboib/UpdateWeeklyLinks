#!/usr/bin/python
# base code stolen from /u/GoldenSights
import praw
import time
import sqlite3
import re
import sys
import tweepy
import datetime



confData = {}

f = open('uwl.conf', 'r')
buf = f.readlines()
f.close()


for b in buf:
    if b[0] == '#' or len(b) < 5 or ":" not in b:
        continue

    confData[b[:b.find(":")]] = b[b.find(":")+1:].strip()


if not confData['username'] or not confData['password']:
    print ("Missing param from conf file")
    quit()



SUBREDDIT = "books"


now=datetime.datetime.now()
print ("\n============\n"+now.strftime("%Y-%m-%d %H:%M"))


sql = sqlite3.connect('UpdateWeeklyLinks.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')
sql.commit()

r = praw.Reddit("UpdateWeeklyLinks v1.0 /u/" + confData['username'])
r.config.decode_html_entities = True


Trying = True
while Trying:
    try:
        r.login(confData['username'], confData['password'])
        Trying = False
    except praw.errors.InvalidUserPass:
        print('Wrong Username or Password')
        quit()
    except Exception as e:
        print("%s" % e)
        time.sleep(5)



def doTwitter (msg):
    try:
        print ("tweeting...")
        print (msg)

        if len(msg) > 138:
            msg = msg[:136] + "..."
            print ("msg too long")
            print("new msg: " + msg)
            print ("new msg len: " + str(len(msg)))

        auth = tweepy.OAuthHandler(confData['twitter_consumer_key'], confData['twitter_consumer_secret'])
        auth.set_access_token(confData['twitter_access_key'], confData['twitter_access_secret'])
        api = tweepy.API(auth)
        api.update_status(msg)
    except Exception as e:
        print ("exception doTwitter() %s" % e)



def scan():
    print('Scanning ' + SUBREDDIT)
    sr = r.get_subreddit(SUBREDDIT)
    posts = sr.get_new(limit=30)
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
            if "Weekly Recommendation Thread for the week of".lower() in post.title.lower():
                weeklyRecThread = True
                searchx = "\[Weekly Recommendation Thread\]\((.*?)\)"

            elif "What books are you reading this week?".lower() in post.title.lower():
                weeklyReadingThread = True
                searchx = "\[Weekly \"What Are You Reading\?\" Thread!\]\((.*?)\)"

            else:
                if post.link_flair_text.lower() == "weeklythread":
                    twitText = '%s: Today in /r/books: "%s"' % (post.short_link, post.title)
                    doTwitter(twitText)



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

                    sb = sr.get_settings()["description"]

                    print ("searchx: " + searchx)
                    matchObj = re.search(searchx, sb)

                    if matchObj:
                       print ("Old url : ", matchObj.group(1))
                       print ("New url : ", post.short_link)

                       new_sb = sb.replace(matchObj.group(1), post.short_link)
                       sr.update_settings(description = new_sb)

                       if weeklyReadingThread:
                           msg = "What are you reading this week? " + post.short_link
                       elif weeklyRecThread:
                           msg = "Looking for good book recommendations? " + post.short_link
                       doTwitter(msg)

                    else:
                       print ("No match!!")
                else:
                    print("Already in db - no action")



try:
    scan()
except Exception as e:
    print('An error has occured:', e)
print ("Finished")



