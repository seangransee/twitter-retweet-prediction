# python crossval.py -a text -n 30 -f results.png > `date "+results-%Y-%m-%d-%H-%M-%S".txt`

import pymongo
from numpy import mean
import argparse
from random import sample
from pylab import show, title, hist, xlabel, ylabel, savefig, figure
from predictor import buildModel, predictor

parser = argparse.ArgumentParser(description='Run a regression on user(s) for a given attribute.')
parser.add_argument('-u', '--users', type=str, nargs='+', help='Username(s) to analyze separated by spaces. Omit to run on all users.')
parser.add_argument('-n', action='store', dest='num_val', type=int, default=30, help='n number for n-fold-validations')
parser.add_argument('-l', '--limit', type=int, help='Number of users to analyze. Useful when ommiting -u.')
parser.add_argument('-a', '--attributes', type=str, nargs='+', help='Attributes to consider', default=["text"])
parser.add_argument('-f', '--file', type=str, help='Where to save figure')
args = parser.parse_args()

conn = pymongo.Connection('mongodb://seanalexryan:machinelearning@ds043027.mongolab.com:43027/twitterdata')
db = conn['twitterdata']

#sets the number n of n-fold-validations, and defaults to 30.
n = args.num_val

if args.users:
    users = args.users
else:
    users = list(db.tweets.find().distinct("user"))
    if args.limit:
        users = users[:args.limit]

improvements = []

print "Users: " + str(len(users)) + "\n" + str(n) + "-fold cross validation\n\n"

for user in users:

    print "USER: " + user

    tweets = list(db.tweets.find({"user": user.lower()}).sort('time'))

    tweetssize = len(tweets)
    binsize = tweetssize / n  # for integers this automatically gives the floor rounding, so no need to change this

    #creates a list of random sublists of all the user's tweets
    allbins = []
    for index in range(n):
        bin = sample(tweets, binsize)  # takes a random sample of tweets list with size binsize
        for items in bin:
            tweets.remove(items)  # remove the sample selected from the list of tweets, so we don't have the same tweet appear in multiple bins
        allbins.append(bin)

    predictorSquaredErrors = []
    baselineSquaredErrors = []

    for i in range(n):
        #generate the testing and training sets for this fold of the validations
        testing = allbins[i]
        training = []
        for bin in allbins:
            if bin != testing:
                training.extend(bin)  # add the bin to the training set if it is not the testing bin, which yields n-1 bins for training and 1 bin for testing

        model = buildModel(training, args.attributes)

        for tweet in testing:
            prediction = predictor(tweet, model)
            actual = tweet['score']

            squaredError = (prediction - actual) ** 2
            predictorSquaredErrors.append(squaredError)

            baselineSquaredError = actual ** 2
            baselineSquaredErrors.append(baselineSquaredError)

    predictorMSE = mean(predictorSquaredErrors)
    baselineMSE = mean(baselineSquaredErrors)

    improvement = ((baselineMSE - predictorMSE) / baselineMSE) * 100
    improvements.append(improvement)

    print "Baseline mean squared error: " + str(baselineMSE)
    print "Prediction mean squared error: " + str(predictorMSE)
    print "Improvement " + str(improvement) + "%\n\n"

if not args.users:

    print "AVERAGE IMPROVEMENT: " + str(mean(improvements)) + "%"

    figure(1, figsize=(15,10))
    hist(improvements)
    xlabel("% improvement over baseline")
    ylabel("Number of users")
    title("Users: " + str(len(users)) + "\n" + str(n) + "-fold cross validation\nAverage improvement above baseline: " + str(mean(improvements)) + "%")
    if args.file:
        savefig(args.file)
    else:
        show()