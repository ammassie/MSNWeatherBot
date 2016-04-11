
# coding: utf-8

# In[1]:

import tweepy, random


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

def suggestions(api):
    suggestionsTweet = ["While you mortals can't change your genetic code, I can! Let me know if there's anything weather related you'd like me to post.",
                        "Let me know how I'm doing - I'm always up for suggestions or improvements!"]
    try:
        api.update_status(status=random.choice(suggestionsTweet))
    except tweepy.error.TweepError:
        print ("Twitter error raised")


# In[4]:

suggestions(api)

