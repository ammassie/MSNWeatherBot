
# coding: utf-8

# In[1]:

import tweepy, feedparser


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

def DaneCoAlerts(api):

    alerts = feedparser.parse('http://alerts.weather.gov/cap/wwaatmget.php?x=WIC025&y=0.rss') #RSS feed from Dane County NWS alerts
    titles = [] #titles from the RSS feed (weather alerts)
    links = [] #Links to the NWS feed
    recentTweets = [] #list of recent tweets
    time_recentTweets = [] #list of times the tweets were created
    repeat = False #boolean to check if weather alert has already been tweeted
    tweet = ''
    for status in tweepy.Cursor(api.user_timeline,id='MSNWeatherBot').items(8): #grabs at the last 8 tweets
        recentTweets.append(status.text)
        time_recentTweets.append(status.created_at)

    for i in range(len(alerts.entries)): #for each current alert on the feed, loops through one by one
        titles.append(alerts.entries[i].title) #append the titles (used as the tweet text)
        links.append(alerts.entries[i].link) #append the links to attach at the end of the tweet
        
        for j in range(len(recentTweets)): #checks to see if that weather alert currently listed on the RSS feed has been tweeted
            if titles[i] == recentTweets[j]: #if the titles are the same, it's a repeat, don't tweet again
                repeat = True
                time_of_tweet = time_recentTweets[j]
                print "The alert " + str(titles[i]) + " was already tweeted on " + str(time_of_tweet) + " UTC"
            elif titles[i] == "There are no active watches, warnings or advisories":
                repeat = True
            else: #if the current alert exists and isn't a repeat, it'll go into this loop
                tweet = titles[i] + " " + links[i]
                repeat = False
    #within the first for loop (for i in...) because then it'll go into the next loop for each alert, can tweet out more than one active alert
        if repeat == False:
            try:
                print tweet
                api.update_status(status=tweet)
            except tweepy.error.TweepError:
                print("Twitter error raised")
        else:
            print 'There are no new active watches, warnings or advisories.'


# In[4]:

DaneCoAlerts(api)

