
# coding: utf-8

# In[187]:

import numpy as np
import urllib2, tweepy
import matplotlib.pyplot as plt
from datetime import datetime
import datetime as dat
plt.rc('font',family='Century Gothic')


# In[188]:

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


# In[189]:

def getModelData(link): #gets lists of all of the important MOS variables (temps, winds, etc.) for the next 3 days
    modelOutput = urllib2.urlopen(link)
    for i in range(6):
        lines = modelOutput.readline() #deletes trash lines in beginning
        if i == 5:
            string_date = lines[24:37].replace(' ', '')
            date = datetime.strptime(string_date, "%m/%d/%Y").date()
            
            runtime = lines[39:43]
            
    modelData = modelOutput.readlines()
    modelOutput.close()
    del modelData[17:] #deletes trash lines at end
    ## storing variables in lists, which will be returned and accessed outside function
    
    #get Hours
    hours = modelData[1].split()
    del hours[0]
    for i in range (len(hours)-2):
        hours[i] = int(hours[i])
        hours[i+1] = hours[i] + 3 
    for i in range ((len(hours)-2), (len(hours))):
        hours[i] = hours[i-1] + 6
    
    
    #Get Temps
    temps = modelData[3].split()
    del temps[0]
    for i in range (len(temps)):
        temps[i] = int(temps[i])
    
    
    #get Wind (speed & direction)
    ##wind speed
    wind = modelData[7].split()
    del wind[0]
    for i in range(len(hours)):
        wind[i] = int(wind[i])
        #wind[i] = wind[i]*1.15077945 # convert to mph
    
    ## wind direction    
    xWind = []
    yWind = []

    windDirection = modelData[6].split()
    del windDirection[0]
    for i in range(len(windDirection)):
        windDirection[i] = int(windDirection[i])*10
        xWind.append(wind[i]*np.cos(np.radians(windDirection[i])))
        yWind.append(wind[i]*np.sin(np.radians(windDirection[i])))

    
    ## get dew point
    dewpoints = modelData[4].split()
    del dewpoints[0]
    for i in range (len(dewpoints)):
        dewpoints[i] = int(dewpoints[i])
        
        
    ## get probability of precipitation in 6 hour period
    pop6 = modelData[8].split()
    del pop6[0]
    count = 0
    pop = []

    for i in range (len(hours)):
        if hours[i] % 6 == 0:
            if i == 0:
                pop.append(0)
            else:
                pop.append(int(pop6[count]))
                count = count + 1
        else:
            pop.append(0)
            
    return hours, temps, wind, xWind, yWind, dewpoints, pop, date


# In[190]:

def daydata(link, day): #takes all of the data, and splits it up into forecasts for day 1, 2, and 3
    hours, temps, wind, xwind, ywind, dewpoint, pops6, date = getModelData(link)
    
    cst = []
    for i in range(len(hours)):
        cst.append(hours[i]-5)
    dayhours = []
    daytemp = [] #for day 1, 2, 3, etc
    daywind = []
    dayxwind = []
    dayywind = []
    daydewpoint = []
    daypops6 = []
    RH = []
    #esat Td/ esat T = RH
    def esat(TF):
        TC = (TF - 32.0)*5/9
        return(611.2*np.exp(17.67*TC/(TC+243.5)))   # Bolton formula
    
    for i in range(len(hours)):
        if day == 1:
            if cst[i] <= 25:
                dayhours.append(cst[i])
                daytemp.append(temps[i])
                daywind.append(wind[i])
                dayxwind.append(xwind[i])
                dayywind.append(ywind[i])
                daydewpoint.append(dewpoint[i])
                RH.append(100*esat(dewpoint[i])/esat(temps[i]))
                daypops6.append(pops6[i])
        elif day == 2:
            if cst[i] >= 22 and cst[i] <= 49:
                dayhours.append(cst[i])
                daytemp.append(temps[i])
                daywind.append(wind[i])
                dayxwind.append(xwind[i])
                dayywind.append(ywind[i])
                daydewpoint.append(dewpoint[i])
                RH.append(100*esat(dewpoint[i])/esat(temps[i]))
                daypops6.append(pops6[i])
        elif day == 3:
            if cst[i] >= 46 and cst[i] <= 74:
                dayhours.append(cst[i])
                daytemp.append(temps[i])
                daywind.append(wind[i])
                dayxwind.append(xwind[i])
                dayywind.append(ywind[i])
                daydewpoint.append(dewpoint[i])
                RH.append(100*esat(dewpoint[i])/esat(temps[i]))
                daypops6.append(pops6[i])
    return dayhours, daytemp, daywind, dayxwind, dayywind, daydewpoint, date, RH, daypops6


# In[191]:

def plotModelOutput(api): #Plots the data
    
    gfsLink = "http://www.nws.noaa.gov/cgi-bin/mos/getmav.pl?sta=KMSN"
    namLink = "http://www.nws.noaa.gov/cgi-bin/mos/getmet.pl?sta=KMSN"

    #day 1
    gfsHours1, gfsTemps1, gfsWind1, gfsXWind1, gfsYWind1, gfsDewpoints1, day1, gfsRH1, gfsPoP1 = daydata(gfsLink, 1)
    namHours1, namTemps1, namWind1, namXWind1, namYWind1, namDewpoints1, day1, namRH1, namPoP1 = daydata(namLink, 1)
    #day2
    gfsHours2, gfsTemps2, gfsWind2, gfsXWind2, gfsYWind2, gfsDewpoints2, day1, gfsRH2, gfsPoP2 = daydata(gfsLink, 2)
    namHours2, namTemps2, namWind2, namXWind2, namYWind2, namDewpoints2, day1, namRH2, namPoP2 = daydata(namLink, 2)
    #day3
    gfsHours3, gfsTemps3, gfsWind3, gfsXWind3, gfsYWind3, gfsDewpoints3, day1, gfsRH3, gfsPoP3 = daydata(gfsLink, 3)
    namHours3, namTemps3, namWind3, namXWind3, namYWind3, namDewpoints3, day1, namRH3, namPoP3 = daydata(namLink, 3)
    
    def xlabels(startday, endday): #gets the x labels for each subplot
        hours = np.arange(24*startday,  24*endday, 6)
        labels = []
        for i in range(len(hours)):
            labels.append(str(hours[i]-24*startday) + ':00')
        return hours, labels
    
    #for axis scaling
    maxT = max(max(gfsTemps1), max(gfsTemps2), max(gfsTemps3), max(namTemps1), max(namTemps2), max(namTemps3))
    minDewpoint = min(min(gfsDewpoints1), min(gfsDewpoints2), min(gfsDewpoints3), min(namDewpoints1),
                     min(namDewpoints2), min(namDewpoints3))
    maxWind = max(max(gfsWind1), max(gfsWind2), max(gfsWind3), max(namWind1), max(namWind2), max(namWind3))
    
    hours, xlabel = xlabels(0,1)
    
    fig = plt.figure(figsize=(10,8))
    plt.rcParams['xtick.labelsize'] = 17
    plt.rcParams['ytick.labelsize'] = 17
    plt.rcParams['lines.linewidth'] = 3
    plt.rcParams['ytick.color'] = 'k'
    plt.rcParams['xtick.color'] = 'k'
    
    
    ax = fig.add_subplot(111)
    plt.subplots_adjust(hspace=0.7, left = 0.0, right = 0.99, bottom = 0.0, wspace = 0.15)
    plt.style.use('fivethirtyeight')
    plt.title('Model Output Statistics (MOS): Madison, WI\n\n', fontsize = 25, color = 'k', )
    text = """This data is generated from the two major weather models run in the US: the North American 
model (NAM) and the Global Forecast System (GFS). While this data can be beneficial in seeing
what the weather will be like in certain places around the US, it can sometimes lead to
large forecasting errors, which is why this is meant to serve as a GUIDE rather than an
absolute forecast. Check with your local forecasting office for the most accurate weather predictions.
To learn more information about MOS products, check out the following links:
http://www.nws.noaa.gov/mdl/synop/products.php, http://www.nws.noaa.gov/mdl/synop/mavcard.php
To learn how to interpret wind barbs, check out the following link: 
http://weather.rap.ucar.edu/info/about_windbarb.html"""
    ax.text(-0.05, -0.08, text,
        verticalalignment='top', horizontalalignment='left',
        transform=ax.transAxes,
        color='k', fontsize=15)
    plt.axis('off')
    
    #DAY 1 Temperature/Dew Point
    ax1 = fig.add_subplot(2,3,1)
    plt.title('Day 1: ' + str(day1) + '\n'
              + str(min(gfsHours1[0], namHours1[0])) + ':00 - 11:59 PM', fontsize = 17)
    ax1.plot(gfsHours1, gfsTemps1, 'firebrick', label = 'GFS')
    ax1.plot(gfsHours1, gfsDewpoints1, color = 'firebrick', linestyle = '--')  
    plt.axis([min(min(gfsHours1), min(namHours1)), 24, minDewpoint - 5, maxT + 5], fontsize = 15)
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, fontsize = 15, fontweight = 'bold', color = 'k')
    plt.yticks(fontweight = 'bold', color = 'k')
    plt.ylabel("Temperature (F)", fontsize = 15, fontweight = 'bold', color = 'k')
    
    ax2 = ax1.twiny()
    ax2.plot(namHours1, namTemps1, 'slateblue', label = 'NAM')
    ax2.plot(namHours1, namDewpoints1, color = 'slateblue', linestyle = '--')
    plt.axis([min(min(gfsHours1), min(namHours1)), 24, minDewpoint - 5, maxT + 5])
    plt.axis('off')
    plt.legend(bbox_to_anchor=(0.0, 1.0), loc=2, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, fontsize = 15, fontweight = 'bold', color = 'k')
    
    #DAY 1 Winds (unwanted, too many graphs)
    #ax1 = fig.add_subplot(3,3,4)
    #plt.title('Day 1: Wind Speed and Direction.\nValid ' + str(day1) + ' '
    #          + str(min(gfsHours1[0], namHours1[0])) + ':00 - 11:59 PM', fontsize = 18)
    #ax1.bar(gfsHours1, gfsWind1, width = 0.70, color = 'red', label = 'GFS')
    #ax1.bar(np.array(namHours1)-0.70, namWind1, width = 0.70, color = 'b', label = 'NAM')
    #plt.barbs(gfsHours1, 0, gfsXWind1, gfsYWind1, linewidth = 1.25, color = 'red')
    #plt.barbs(namHours1, 0, namXWind1, namYWind1, linewidth = 1.25, color = 'b')
    #plt.hlines(0, 0, max(gfsHours1), color = 'k')
    #plt.axis([min(min(gfsHours1), min(namHours1))-4, 24, 
    #          -10, 10])
    #plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    #plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    #plt.yticks(np.arange(0,max(max(gfsWind1), max(namWind1)), 5), fontweight = 'bold', color = 'k')
    #plt.ylabel("Wind Speed (knots)", fontsize = 15, labelpad = -3, fontweight = 'bold', color = 'k')

     
    #DAY 1 Relative Humidity, precip potential
    ax1 = fig.add_subplot(2,3,4)
    plt.title('Day 1: '
              + str(day1) + '\n' + str(min(gfsHours1[0], namHours1[0])) + ':00 - 11:59 PM', fontsize = 17)
    ax1.plot(gfsHours1, gfsRH1, 'firebrick')
    plt.axis([min(min(gfsHours1), min(namHours1)), 24, 0, 100])
    ax1.bar(gfsHours1, gfsPoP1, width = 0.70, color = 'firebrick', label = 'GFS')
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    plt.ylabel("(%)", fontsize = 15, labelpad = -4, fontweight = 'bold', color = 'k')
    plt.yticks(np.arange(0,101,20), fontweight = 'bold', color = 'k')
    
    ax2 = ax1.twiny()
    ax2.plot(namHours1, namRH1, 'slateblue')
    ax2.bar(np.array(namHours1)-0.70, namPoP1, width = 0.70, color = 'slateblue', label = 'NAM')
    plt.barbs(gfsHours1, -20, gfsXWind1, gfsYWind1, linewidth = 3, color = 'firebrick')
    plt.barbs(namHours1, -20, namXWind1, namYWind1, linewidth = 3, color = 'slateblue')
    plt.hlines(0, min(min(gfsHours1), 0), max(gfsHours1), color = 'k')
    plt.axis([min(min(gfsHours1), min(namHours1)), 24, -50, 100])
    plt.axis('off')
    plt.legend(bbox_to_anchor=(0.0, 1.0), loc=2, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, color = 'k')
    
    #DAY 2 Temperature/Dew Point
    ax1 = fig.add_subplot(2,3,2)
    plt.title('Temperature & Dew Point\nDay 2: ' + str(day1 + dat.timedelta(days=1))
              + '\n12:00 AM - 11:59 PM', fontsize = 17)
    ax1.plot(gfsHours2, gfsTemps2, 'firebrick', label = 'GFS')
    ax1.plot(gfsHours2, gfsDewpoints2, color = 'firebrick', linestyle = '--')
    plt.axis([24, 48, minDewpoint - 5, maxT + 5])
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    hours, xlabel = xlabels(1,2) 
    plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    plt.yticks(fontweight = 'bold', color = 'k')
    plt.xlabel("Time (CST)", fontsize = 15, labelpad = 5, fontweight = 'bold', color = 'k')

    ax2 = ax1.twiny()
    ax2.plot(namHours2, namTemps2, 'slateblue', label = 'NAM')
    ax2.plot(namHours2, namDewpoints2, color = 'slateblue', linestyle = '--')
    plt.axis([24, 48, minDewpoint - 5, maxT + 5])
    plt.axis('off')
    plt.legend(bbox_to_anchor=(0.0, 1.0), loc=2, borderaxespad=0, fontsize = 12)
    
    #DAY 2 winds
    #ax1 = fig.add_subplot(3,3,5)
    #plt.title('Day 2: Wind Speed and Direction.\nValid ' + str(day1 + dat.timedelta(days=1))
    #          + ' 12:00 AM - 11:59 PM', fontsize = 18)
    #ax1.bar(gfsHours2, gfsWind2, width = 0.70, color = 'red', label = 'GFS')
    #ax1.bar(np.array(namHours2)-0.70, namWind2, width = 0.70, color = 'b', label = 'NAM')
    #plt.barbs(gfsHours2, 0, gfsXWind2, gfsYWind2, linewidth = 1.25, color = 'red')
    #plt.barbs(namHours2, 0, namXWind2, namYWind2, linewidth = 1.25, color = 'b')
    #plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    #plt.axis([22.25, 48, -10, 10])
    #plt.hlines(0, 0, 48, color = 'k')
    #plt.yticks(np.arange(0,max(max(gfsWind1), max(namWind1)), 5), fontweight = 'bold', color = 'k')
    #plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    #plt.xlabel("Time (CST)", fontsize = 15, labelpad = 5, fontweight = 'bold', color = 'k')
    
    #DAY 2 Relative Humidity, precip potential
    ax1 = fig.add_subplot(2,3,5)
    plt.title('Relative humidity (line),chance of precipitation in the previous 6 hour period (bar),\nand wind barbs (knots).\nDay 2: ' 
              + str(day1 + dat.timedelta(days=1)) + '\n12:00 AM - 11:59 PM', fontsize = 17)
    ax1.plot(gfsHours2, gfsRH2, 'firebrick')
    plt.axis([24, 48, 0, 100])
    ax1.bar(gfsHours2, gfsPoP2, width = 0.70, color = 'firebrick', label = 'GFS')
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    plt.xlabel("Time (CST)", fontsize = 15, labelpad = 5, fontweight = 'bold', color = 'k')
    plt.yticks(np.arange(0,101,20), fontweight = 'bold', color = 'k')
    
    ax2 = ax1.twiny()
    plt.barbs(gfsHours2, -20, gfsXWind2, gfsYWind2, linewidth = 3, color = 'firebrick')
    plt.barbs(namHours2, -20, namXWind2, namYWind2, linewidth = 3, color = 'slateblue')
    plt.hlines(0,0,48, color = 'k')
    ax2.plot(namHours2, namRH2, 'slateblue')
    ax2.bar(np.array(namHours2)-0.70, namPoP2, width = 0.70, color = 'slateblue', label = 'NAM')
    plt.axis([24, 48, -50, 100])
    plt.axis('off')
    plt.legend(bbox_to_anchor=(0.0, 1.0), loc=2, borderaxespad=0, fontsize = 12)

    
    #DAY 3 Temperature/Dew Point
    hours, xlabel = xlabels(2,3)
    ax1 = fig.add_subplot(2,3,3)
    plt.title('Day 3: ' + str(day1 + dat.timedelta(days=2))
              + '\n12:00 AM - 11:59 PM', fontsize = 17)
    ax1.plot(gfsHours3, gfsTemps3, 'firebrick', label = 'GFS')
    ax1.plot(gfsHours3, gfsDewpoints3, color = 'firebrick', linestyle = '--')
    plt.axis([48, 72, minDewpoint - 5, maxT + 5])
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    plt.yticks(fontweight = 'bold', color = 'k')    
    
    ax2 = ax1.twiny()
    ax2.plot(namHours3, namTemps3, 'slateblue', label = 'NAM')
    ax2.plot(namHours3, namDewpoints3, color = 'slateblue', linestyle = '--')    
    plt.axis([48, 72, minDewpoint - 5, maxT + 5])
    plt.axis('off')
    plt.legend(bbox_to_anchor=(0.0, 1.0), loc=2, borderaxespad=0, fontsize = 12)
    
    #DAY 3 winds
    #ax1 = fig.add_subplot(3,3,6)
    #plt.title('Day 3: Wind Speed and Direction.\nValid ' + str(day1 + dat.timedelta(days=2))
    #          + ' 12:00 AM - 11:59 PM ', fontsize = 18)
    #ax1.bar(gfsHours3, gfsWind3, width = 0.70, color = 'red', label = 'GFS')
    #ax1.bar(np.array(namHours3)-0.70, namWind3, width = 0.70, color = 'b', label = 'NAM')
    #plt.barbs(gfsHours3, 0, gfsXWind3, gfsYWind3, linewidth = 1.25, color = 'red')
    #plt.barbs(namHours3, 0, namXWind3, namYWind3, linewidth = 1.25, color = 'b')
    #plt.hlines(0, 0, 73, color = 'k')
    #plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    #plt.axis([46.5, 72, -10, 10])
    #plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    #plt.yticks(np.arange(0,max(max(gfsWind3), max(namWind3)), 5), fontweight = 'bold', color = 'k')
   
    #DAY 3 Relative Humidity, precip potential
    ax1 = fig.add_subplot(2,3,6)
    plt.title('Day 3: ' 
              + str(day1 + dat.timedelta(days=2)) + '\n12:00 AM - 11:59 PM', fontsize = 16)
    ax1.plot(gfsHours3, gfsRH3, 'firebrick')
    plt.axis([46.5, 72, 0, 100])
    ax1.bar(gfsHours3, gfsPoP3, width = 0.70, color = 'firebrick', label = 'GFS')
    plt.legend(bbox_to_anchor=(1.0, 1.0), loc=1, borderaxespad=0, fontsize = 12)
    plt.xticks(hours, xlabel, fontweight = 'bold', color = 'k')
    plt.yticks(np.arange(0,101,20),fontweight = 'bold', color = 'k')
    
    ax2 = ax1.twiny()
    ax2.plot(namHours3, namRH3, 'slateblue')
    ax2.bar(np.array(namHours3)-0.70, namPoP3, width = 0.70, color = 'slateblue', label = 'NAM')
    plt.barbs(gfsHours3, -20, gfsXWind3, gfsYWind3, linewidth = 3, color = 'firebrick')
    plt.barbs(namHours3, -20, namXWind3, namYWind3, linewidth = 3, color = 'slateblue')
    plt.hlines(0, 0, 73, color = 'k')
    plt.axis([46.5, 72, -50, 100])
    plt.axis('off')
    plt.legend(bbox_to_anchor=(0.0, 1.0), loc=2, borderaxespad=0, fontsize = 12)
    
    plt.savefig('ModelData.png', bbox_inches = 'tight', facecolor = 'lightgray')
    
    tweet = "It's the MOSt important time of the day! Here's what the models are forecasting for the next few days."
    try:
        #plt.show()
        api.update_with_media("ModelData.png", status=tweet)
        print 'Tweet successful!'
    except tweepy.error.TweepError:
        print ("Twitter error raised")
    except HTTPError:
        print ("URL Error")
    
    plt.close('all')


# In[192]:

plotModelOutput(api)

