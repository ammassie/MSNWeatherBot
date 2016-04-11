
# coding: utf-8

# In[2]:

import tweepy


# In[3]:

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


# In[4]:

def followFollowers(api): #auto follows those who follow MSNWeatherBot
    followers = api.followers_ids('MSNWeatherBot') #user IDs
    #print followers    
    screen_names = [] #list of twitter handles

    for i in range(len(followers)):
        userID = followers[i]
        u = api.get_user(userID)
        screen_names.append(u.screen_name)

    following = api.friends_ids('MSNWeatherBot')
    newFollowing = []
    count = 0
    for i in range(len(followers)):
        if followers[i] not in following:
            try:
                api.create_friendship(followers[i])
                newFriend = api.get_user(followers[i])
                newFollowing.append(newFriend.screen_name)
                count = count + 1
            except tweepy.error.TweepError:
                print ("Twitter error raised")

    print "Successfully followed " + str(count) + " user(s)."
    print newFollowing


# In[5]:

followFollowers(api)

