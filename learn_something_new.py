
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

def learnSomethingNew(api):
    eduLinks = ["http://www.cpc.noaa.gov/", "http://cimss.ssec.wisc.edu/goes/blog/", "http://www.aos.wisc.edu/weather/", 
                "http://www.srh.noaa.gov/jetstream/", "http://www.theweatherprediction.com", "http://earth.nullschool.net", 
                "http://www.atoptics.co.uk/opod.htm", "http://www.ssec.wisc.edu/data/us_comp/movie-large.php?loop=true", 
                "https://weatherspark.com/#!graphs;ws=30954", "http://wxguys.ssec.wisc.edu/", "http://www.weather.gov/owlie/"]
    tweet = "Want to learn something new about weather today? Why not learn it here: " + random.choice(eduLinks)
    print tweet
    try:
        api.update_status(status=tweet)
    except tweepy.error.TweepError:
        print("Twitter error raised")
    except HTTPError:
        print ("URL error raised")
        


# In[4]:

learnSomethingNew(api)

