
# coding: utf-8

# In[33]:

from MesoPy import Meso
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import tweepy


# In[34]:

# Authenticate Twitter Session
f = open('MSNWeatherBot_authentication.txt','r')
keys = f.readlines()
consumer_key = keys[0].replace('\n', '')
consumer_secret = keys[1].replace('\n', '')
access_key = keys[2].replace('\n', '')
access_secret = keys[3].replace('\n', '')
MesoPy_token = keys[4].replace('\n', '')
f.close()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


# In[35]:

def pastMonthObs(): #gets the obs from Mesopy from the last month
    d = datetime.now() - timedelta(1) #going back into last month, because we want to look back on the month that just passed
    lastmonth = '%02d' % d.month #so the month is formatted correctly
    year = '%04d' % d.year
    lastday = '%02d' % d.day
    start = str(year) + str(lastmonth) + str('01') + '0000' #start at 00 UTC 
    end = str(year) + str(lastmonth) + str(lastday) + '2359' #end at end of month
    
    m = Meso(token=MesoPy_token)
    data = []
    time = m.timeseries(stid='kmsn', start=start, end=end)
    kmsn = time['STATION'][0] #KMSN station
    rawtemps = kmsn['OBSERVATIONS']['air_temp_set_1']
    rawobstime = kmsn['OBSERVATIONS']['date_time']
    time = []
    temps = [] #in fahrenheit
    for i in range(len(rawobstime)):
        t = str(rawobstime[i]).replace('T', ' ').replace('Z', '')
        dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        time.append(mdates.date2num(dt))
        temps.append('%.2f' % float(rawtemps[i] * 9/5 + 32)) #converts from celsius to fahrenheit
        
    return temps, time


# In[36]:

####
# This module here gets the climate normals for Madison, WI Dane County Regional Airport. The code below shows how 
# to get these normals from the NCDC/NOAA Website. I decided to download this file rather than call the website every time.
####
####
####
####
#
#link = 'http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/products/hourly/hly-temp-normal.txt'
#import urllib2
#lines = (urllib2.urlopen(link)).readlines()
#
####
#### The following code is what I used to obtain the data for Madison specifically - it only needs to be run once
####
#kmsn_data = []
#f = open('hly-temp-normal.txt','r')
#for line in f.readlines():
#    if 'USW00014837' in line: #this is the code for the Madison Dane County Regional Airport
#        kmsn_data.append(line)
#with open('KMSN_Temp_Normals.txt', 'w') as file: #this writes a file for just the KMSN normals
#    for line in kmsn_data:
#        file.write("{}".format(line))
#    file.close()
####


# In[37]:

def climateNormals():
    file = open('KMSN_Temp_Normals.txt', 'r')
    data = file.readlines()
    file.close()
    d = datetime.now() - timedelta(1) #going back into last month, because we want to look back on the month that just passed
    lastmonth = '%02d' % d.month #so the month is formatted correctly
    #lastmonth = '02'
    alltimes = []
    alltemps = []
    for i in range(len(data)): 
        tlist = data[i].split() #makes the line a list of strings
        for j in range(0,24,1):        
            day = str(tlist[1]) + '/' + str(tlist[2]) #pulls out the month and date in the form MM/DD
            hour = str('%02d' % j) #pulls out the hour of the climate normal
            alltimes.append(day + ' ' + hour + ':00') #appends the time of the climate normal in the form MM/DD HH:00
            hourly_temp = tlist[j+3] #offsets to accomodate the fact that the temperature data isn't what's first in the file
            alltemps.append(hourly_temp.replace('C', '')) #appends temp data, removes C from end (which stands for complete record)

    temp = [] #for the specific month
    time = [] #for the specific month
    for i in range(len(alltimes)):
        if alltimes[i].startswith(lastmonth): #pulls out data from last month
            dt = datetime.strptime(alltimes[i], "%m/%d %H:%M")
            time.append(dt)
            temp.append(int(alltemps[i])/10)


    return temp, time


# In[54]:

def plotAndTweet(api):
    current_temp, current_time = pastMonthObs()
    normal_temp, normal_time = climateNormals()
    plt.style.use('fivethirtyeight')
    fig = plt.figure(figsize=(20,10))
    plt.rcParams['xtick.labelsize'] = 15
    plt.rcParams['ytick.labelsize'] = 17
    plt.rcParams['lines.linewidth'] = 3
    ax1 = fig.add_subplot(1,1,1)
    ax1.plot_date(current_time, current_temp, 'b-', label = "Last Month")
    plt.xlabel('Date', fontsize=17)
    plt.ylabel('Temperature (F)', fontsize=17)
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 16)
    
    ax2 = ax1.twiny()
    ax2.plot_date(normal_time, normal_temp, 'r-', label = "Climate Normal")
    plt.axis('off')
    plt.legend(bbox_to_anchor=(1.0, 0.95), loc=1, borderaxespad=0, fontsize = 16)
    plt.title("Last month's weather versus the climate normal: Madison, WI", fontsize = 20, loc = 'center')
    text = """The plot above shows temperature observations from the Dane County Regional Airport from the past month, along with climate normals
from 1981-2010. Current observations are retrieved from MesoWest/SynopticLabs, and climate normals are retrieved from NOAA.
Learn more about historical weather in your area here:
http://w2.weather.gov/climate/          https://www.wunderground.com/history/          https://weatherspark.com/#!graphs;a=USA/WI/Madison"""
    ax1.text(0.985, 0.015, text, verticalalignment = 'bottom', horizontalalignment = 'right',
             transform=ax2.transAxes, fontsize = '16', bbox=dict(facecolor='whitesmoke', alpha = 0.5))
    #plt.show()
    plt.savefig('Climate_Norm.png', bbox_inches = 'tight')
    tweet = "Here's last month's weather compared to the 30-year average for Madison. How anomalous was this month's weather?"
    try:
        #print 'Climate_Norm.png'
        api.update_with_media("Climate_Norm.png", status = tweet)
    except tweepy.error.TweepError:
        print ("Twitter error raised")
    plt.close('all')


# In[55]:

plotAndTweet(api)

