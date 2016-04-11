
# coding: utf-8

# In[13]:

import feedparser, tweepy


# In[14]:

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


# In[15]:

def CIMSS_tweet(api):
    posts = feedparser.parse('http://cimss.ssec.wisc.edu/goes/blog/feed') #grabs the posts from the CIMSS blog
    initialTitle = posts.entries[0].title #list of the title of the post
    link = posts.entries[0].link #list of the link to the post
    
#Shortening title to fit 140 character limit for Twitter
    if len(initialTitle) >= 74: #title cannot be greater than 74 characters
        #74 char here + 43 char with tweet intro below + 23 char with auto-shortened link = 140
        final_title = initialTitle[0:73]
    else:
        final_title = posts.entries[0].title 
    
#checking to see if this blog post has already been tweeted        
    recentTweets = [] #list of recent tweets
    time_recentTweets = [] #list of times the tweets were created
    repeat = False #boolean to check if weather alert has already been tweeted
    
    for status in tweepy.Cursor(api.user_timeline,id='MSNWeatherBot').items(15): #grabs the last 15 tweets
        recentTweets.append(status.text)
        time_recentTweets.append(status.created_at)
    
    for i in range(len(recentTweets)): #for each of the recent tweets
        if final_title in recentTweets[i]: #if the blog post title is contained in a recent tweet, repeat = true
            repeat = True
            time_of_tweet = time_recentTweets[i] #time this CIMSS blog post was tweeted
      
    tweet = 'The latest from the CIMSS satellite blog: ' + final_title + ' ' + link
    if repeat == False:
        try:
            print tweet
            api.update_status(status=tweet)
        except tweepy.error.TweepError:
            print("Twitter error raised")
    else:
        print "This blog post was already tweeted on " + str(time_of_tweet) + " UTC"


# In[16]:

CIMSS_tweet(api)

