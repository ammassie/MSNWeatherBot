
# coding: utf-8

# In[1]:

import tweepy


# In[2]:

# Authenticate Twitter Session
f = open('MSNWeatherBot_authentication.txt','r')
keys = f.readlines()
consumer_key = keys[0].replace('\n', '')
consumer_secret = keys[1].replace('\n', '')
access_key = keys[2].replace('\n', '')
access_secret = keys[3].replace('\n', '')

f.close()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


# In[3]:

def forecastDiscussion(api):
    tweet = "What are the experts saying about the weather this week? Check out the NWS forecast discussions to learn more: http://forecast.weather.gov/product.php?site=mkx&product=AFD&issuedby=MKX"
    try:
        #print tweet
        api.update_status(status=tweet)
    except tweepy.error.TweepError:
        print("Twitter error raised")


# In[4]:

forecastDiscussion(api)

