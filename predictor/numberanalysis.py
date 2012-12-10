import numpy as np
from sklearn.svm import SVR

def getAttributeResult(tweet, attribute):
    if attribute == "timeofday":
        return tweet['time'].hour * 3600 + tweet['time'].minute * 60 + tweet['time'].second
    elif attribute == 'lengthoftweet':
        return len(tweet['text'])
    elif attribute == 'averagewordlength':
        return np.mean(map(lambda x: len(x), tweet['text'].split(' ')))
    elif attribute == 'hashtags':
        return tweet['text'].count('#')
    elif attribute == 'mentions':
        return tweet['text'].count('@')
    elif attribute == 'links':
        return tweet['text'].count('http')
    elif attribute == 'frequency':
        if 'timeSinceLastTweet' in tweet:
            return tweet['timeSinceLastTweet']
        else:
            return 0

def buildNumberModel(tweets, attribute):

    tuples = []

    i = 0
    for tweet in tweets:
        resultOfAttribute = getAttributeResult(tweet, attribute)
        tuples.append((resultOfAttribute, tweet['score']))

    tuples = sorted(tuples, key=lambda tweet: tweet[0])
    i += 1

    x = []
    X = []
    Y = []

    for tweet in tuples:
        x.append(tweet[0])
        X.append([tweet[0]])
        Y.append(tweet[1])

    X = np.asarray(X)
    Y = np.asarray(Y)

    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=5e-10)
    y_rbf = svr_rbf.fit(X, Y).predict(X)

    model = {}
    std = np.std(y_rbf)
    model["model"] = (X, y_rbf)
    model["std"] = std

    return model


def numberAnalysis(tweet, model):

    prediction = 0

    for attribute, value in model.iteritems():

        if attribute != "text":
            x = []
            X = model[attribute]['model'][0]
            Y = model[attribute]['model'][1]
            y = list(Y)
            for n in X:
                x.append(n[0])
            prediction += np.interp(getAttributeResult(tweet, attribute), x, y) * model[attribute]['weight']

    return prediction
