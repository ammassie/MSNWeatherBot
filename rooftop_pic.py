
# coding: utf-8

# In[27]:

import numpy as np
import urllib2, tweepy, random
import matplotlib.pyplot as plt


# In[28]:

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


# In[29]:

# rooftop pic & measurements
def rooftopPic(api):
    imageURLlist = ['http://metobs.ssec.wisc.edu/pub/cache/aoss/cameras/northwest/latest_orig.jpg', 
                    'http://metobs.ssec.wisc.edu/pub/cache/aoss/cameras/west/latest_orig.jpg', 
                    'http://metobs.ssec.wisc.edu/pub/cache/aoss/cameras/north/latest_orig.jpg', 
                    'http://metobs.ssec.wisc.edu/pub/cache/aoss/cameras/east/latest_orig.jpg', 
                    'http://metobs.ssec.wisc.edu/pub/cache/aoss/cameras/south/latest_orig.jpg']
    resource = urllib2.urlopen(random.choice(imageURLlist))
    output = open("rooftop_image.jpg","wb")
    output.write(resource.read())
    output.close()
    
    #get Rooftop Measurements
    rooftopData = urllib2.urlopen("http://metobs.ssec.wisc.edu/app/rig/tower/data/ascii?symbols=t:td:p")

    data = rooftopData.readlines()
    rooftopData.close()

    measurements = data[1].split(',')
    date = measurements[0]
    time = measurements[1]
    temperature = np.around(float(measurements[2])*9/5 + 32, decimals=2)
    dewpoint = np.around(float(measurements[3]) * 9/5 + 32, decimals=2)
    pressure = measurements[4]
    
    tweet = 'Live from the AOS/SSEC rooftop:\nTemperature (F): ' + str(temperature) + '\nDewpoint (F): ' + str(dewpoint) + ' \nPressure (mb): ' + pressure
    try:
        #print tweet
        api.update_with_media("rooftop_image.jpg", status=tweet)
    except tweepy.error.TweepError:
        print ("Twitter error raised")


# In[30]:

rooftopPic(api)

