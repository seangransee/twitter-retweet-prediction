# score_data.py
#
# This file will go through all the tweets of the user(s) you specify
# and assign each tweet a score. If you do not specify any users, it
# will run through the entire dataset.
#
# The "score" is the percentage of retweets above what a "normal" tweet
# would get at that time. The higher the score, the better the tweet.
#
# All other analysis will correlate other attributes with this score.
#
# HOW TO RUN:
#
# python score_data.py                                          (run on all users)
# python score_data.py -u barackobama                           (run on one user)
# python score_data.py -u barackobama justinbieber ladygaga     (run on multiple users)
#
# Once you run this once, there's no need to run it again
# unless you change the scoring algorithm

import pymongo
import argparse
from functions import *

parser = argparse.ArgumentParser(description='Score the Twichr data')
parser.add_argument('-u', '--users', nargs='+', type=str, help='Usernames to analyze')
args = parser.parse_args()

conn = pymongo.Connection('mongodb://seanalexryan:machinelearning@ds043027.mongolab.com:43027/twitterdata')
db = conn['twitterdata']

if args.users:
    users = args.users
else:
    users = list(db.tweets.find().distinct("user"))

for user in users:

    tweets = list(db.tweets.find({"user":user.lower()}).sort('time'))

    if "score" in tweets[0]:
        print "Skipping over " + user
    else:

        if len(tweets) < 50:
            db.tweets.remove({"user": user})
            print "Removed " + user + " from database"
            break

        time_retweets_tuples = []
        for tweet in tweets:
            tweet['timeFloat'] = time_to_float(tweet['time'])
            time_retweets_tuples.append((tweet['timeFloat'], tweet['retweets']))

        m, b = theilsen(time_retweets_tuples)

        i = 0
        for tweet in tweets:
            tweet['timeFloat'] = time_to_float(tweet['time'])
            if i > 0:
                tweet['timeSinceLastTweet'] = tweet['timeFloat'] - tweets[i - 1]['timeFloat']
            i += 1
            tweet['normal'] = m * tweet['timeFloat'] + b
            try:
                tweet['score'] = ((tweet['retweets'] - tweet['normal']) / tweet['normal']) * 100
                db.tweets.save(tweet)
            except:
                db.tweets.remove({"user": user})
                print "Removed " + user + " from database"
                break

        print "Saved scores for " + user