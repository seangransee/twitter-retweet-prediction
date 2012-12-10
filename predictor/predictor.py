from textanalysis import buildDictionary, textAnalysis
from numberanalysis import buildNumberModel


def buildModel(tweets, attributes):

    model = {}

    for attribute in attributes:
        if attribute != "text":
            model[attribute] = buildNumberModel(tweets, attribute)
        else:
            model[attribute] = buildDictionary(tweets)

    sum = 0
    for k, v in model.iteritems():
        if k != "text":
            std = v['std']
            sum += std

    for k, v in model.iteritems():
        if k != "text":
            v['weight'] = v['std'] / sum

    return model


def predictor(tweet, model):

    predictionFromText = 0

    if "text" in model:
        predictionFromText = textAnalysis(tweet['text'], model['text'])

    return predictionFromText
