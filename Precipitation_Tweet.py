
# coding: utf-8

# In[5]:

import numpy as np
import urllib2, tweepy
import matplotlib.pyplot as plt
plt.rc('font',family='Century Gothic')


# In[4]:

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

def getModelPoP(link): #PoP = probability of Precipitation
    modelOutput = urllib2.urlopen(link)
    for i in range(5):
        lines = modelOutput.readline() #deletes trash lines in beginning
    
    modelData = modelOutput.readlines()
    del modelData[18:] #deletes trash lines at end
    
    ## get pop in 6 hour period
    pop6 = modelData[9].split()
    del pop6[0]
    for i in range (len(pop6)):
        pop6[i] = int(pop6[i])
    return pop6


# In[7]:

def POP6radarTweet(api):
    gfsLink = "http://www.nws.noaa.gov/cgi-bin/mos/getmav.pl?sta=KMSN"
    namLink = "http://www.nws.noaa.gov/cgi-bin/mos/getmet.pl?sta=KMSN"
    gfsPOP6 = getModelPoP(gfsLink)
    namPOP6 = getModelPoP(namLink)
    
    pop6tweet = "There's a chance of precipitation in the forecast. Follow the radar here (via UW AOS/SSEC) http://tempest.aos.wisc.edu/radar/us3comphtml5.html"

    if gfsPOP6[0] >= 50 or namPOP6[0] >= 50:
        try:
            midwestRadarURL = urllib2.urlopen("http://tempest.aos.wisc.edu/radar/mw3comp.gif")
            midwestRadar_output = open("Midwest_Radar.gif", "wb")
            midwestRadar_output.write(midwestRadarURL.read())
            midwestRadar_output.close()
            api.update_with_media("Midwest_Radar.gif", status=pops6tweet)
        except tweepy.error.TweepError:
            print ("Twitter error raised")


# In[8]:

POP6radarTweet(api)

