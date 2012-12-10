# textanalysis.py
#
# python textanalysis.py -u justinbieber selenagomez

import re
from numpy import mean


def getWords(tweet):
    words = []
    for word in tweet.split(' '):
        word = re.sub('[^0-9a-zA-Z]+', '', word.lower())
        if word[:4] != "http" and word[:3] != "www" and len(word) > 2:
            words.append(word)
    return words


def buildDictionary(tweets):
    dictionary = {}
    for tweet in tweets:
        for word in getWords(tweet['text']):
            if word in dictionary:
                dictionary[word].append(tweet['score'])
            else:
                dictionary[word] = [tweet['score']]

    for word in dictionary:
        dictionary[word] = mean(dictionary[word])

    return dictionary


def textAnalysis(tweet, dictionary):

    wordScores = []
    for word in getWords(tweet):
        if word in dictionary:
            wordScores.append(dictionary[word])

    if wordScores:
        score = mean(wordScores)
    else:
        score = 0

    return score


if __name__ == "__main__":

    import operator
    import pymongo
    import argparse

    parser = argparse.ArgumentParser(description='Print the dictionary for a user.')
    parser.add_argument('-u', '--users', type=str, nargs="+", help='Username(s) to analyze separated by spaces. Omit to run on all users.')
    parser.add_argument('-l', '--limit', type=int, help='Number of users to analyze. Useful when ommiting -u.')
    parser.add_argument('-t', '--tweet', type=str, help='Tweet to predict')
    args = parser.parse_args()

    conn = pymongo.Connection('mongodb://seanalexryan:machinelearning@ds043027.mongolab.com:43027/twitterdata')
    db = conn['twitterdata']

    if args.users:
        users = args.users
    else:
        users = list(db.tweets.find().distinct("user"))
        if args.limit:
            users = users[:args.limit]

    for user in users:

        print "USER: " + user + "\n"

        tweets = list(db.tweets.find({"user": user.lower()}).sort('time'))

        dictionary = buildDictionary(tweets)

        sorted_dict = sorted(dictionary.iteritems(), key=operator.itemgetter(1))

        sorted_dict.reverse()

        for item in sorted_dict:
            print str(item[0]) + ": " + str(item[1])+ ": " + str(item[1])

        if args.tweet:
            print "\n\n"
            wordScores = []
            for word in getWords(args.tweet):
                if word in dictionary:
                    print word + ": " + str(dictionary[word])
                    wordScores.append(dictionary[word])

            print "Predicted score: " + str(mean(wordScores))

        print "\n==============\n"
