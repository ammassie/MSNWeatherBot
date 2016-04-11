
# coding: utf-8

# In[8]:

import urllib2, tweepy
import matplotlib.pyplot as plt
plt.rc('font',family='Century Gothic')
from datetime import datetime
from skewt import SkewT
import matplotlib.image as mpimg
import matplotlib.animation as animation
from moviepy.editor import VideoFileClip

GRB = 72645 #ids for UWYO site
MPX = 72649 
DVN = 74455
ILX = 74560


# In[9]:

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


# In[10]:

def getDateTime():
    date = str(datetime.utcnow())
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    return date, year, month, day


# In[11]:

def getSoundingLink(stid):
    date, year, month, day = getDateTime()
    runHour = "12" #we want 00Z run (or else 12Z)
    URL = "http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR=" + str(year) +"&MONTH=" + str(month) + "&FROM=" + str(day) + str(runHour) + "&TO=" + str(day) + str(runHour) + "&STNM=" + str(stid)
    print URL
    return URL


# In[12]:

def plotSkewT(URL, stid):
    date, year, month, day = getDateTime()
    SoundingFile = urllib2.urlopen(URL).read() #reads sounding file
    filename = str(stid) + 'SoundingFile.html'

    with open(filename, 'w') as fid:
        fid.write(SoundingFile)
        fid.close()

    file = open(filename, "r")

# Skip the appropriate number of header lines
    for i in range(12):
        line = file.readline()
        if i ==4:
            #stid = line[4:9]
            dtime = line[40:] 
            stname = line[10:13]
        
# Read remaining lines from file into a list of text lines
    lines = file.readlines()

    file.close()
    pres = []
    temp = []
    dwpt = []
    Zsnd = [] #height
    mixingRatio = []
    wsp = []
    wdir = []

    for line in lines:
        words = line.split()
        if len(words) !=11: #this happens when the pressure level doesn't have a measurement for each variable
            break
        pres.append(float(words[0]))
        temp.append(float(words[2]))
        dwpt.append(float(words[3]))
        Zsnd.append(float(words[1]))
        mixingRatio.append(float(words[5]))   
        wsp.append(float(words[7]))
        wdir.append(float(words[6]))
    dict = {'pres' : pres, 'temp' : temp, 'dwpt': dwpt, 'drct': wdir,'sknt': wsp, 'hght' : Zsnd} #in format for skewT plot
    
    #Plot Data
    fig = plt.figure()
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    ax = fig.add_subplot(111)
    sounding = SkewT.Sounding(soundingdata = dict) #plots skew T
    if stname == 'GRB': #the following if statements are for the title of each graph
        station = 'Green Bay, WI'
    if stname == 'MPX':
        station = 'Chanhassen, MN'
    if stname == 'DVN':
        station = 'Davenport, IA'
    if stname == 'ILX':
        station = 'Lincoln, IL'
    
    sounding.plot_skewt(title = station + ': ' + str(month) + '/' + str(day) + '/' +  str(year) + ' 12Z', lw=3) 

    text = """
Data from UWYO Department of Atmospheric Science (http://weather.uwyo.edu/upperair/sounding.html)
Learn how to interpret soundings here: http://www.wunderground.com/blog/24hourprof/introduction-
    to-skewt-logp-diagrams
"""
    plt.text(-0.15, 0.08, text, verticalalignment = 'top', horizontalalignment='left',
             fontsize = '13',  transform = ax.transAxes)
    plt.savefig(stname + "SkewT.png")

    plt.close()
    
    return stname + "SkewT.png"


# In[13]:

def animate(GRB, MPX, DVN, ILX, api):
    #these get the sounding link for the correct station and plot it
    GRBFile = plotSkewT(getSoundingLink(GRB), GRB)
    MPXFile = plotSkewT(getSoundingLink(MPX), MPX)
    DVNFile = plotSkewT(getSoundingLink(DVN), DVN)
    ILXFile = plotSkewT(getSoundingLink(ILX), ILX)
    
    image = [GRBFile, MPXFile, DVNFile, ILXFile]
    fig = plt.figure(figsize = (9.5,9.5))
    
    #plt.subplots_adjust(top = 1.0, bottom = 0.0) #for appropriate spacing
    def func(image): #needed to animate - this loops through each of the images for the video
        img = mpimg.imread(image)
        line = plt.imshow(img)
        return line
    
    #makes video, so we can later make a gif
    mywriter = animation.FFMpegWriter(fps=0.1) 
    ax = plt.axes(frameon = False)
    plt.tight_layout()
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ani = animation.FuncAnimation(fig, func, image, interval = 20, )
    ani.save('soundingani.mp4',writer=mywriter)
    
    clip = (VideoFileClip('soundingani.mp4'))
    clip.write_gif('soundingani.gif')
    tweet = "Weather balloons give us a snapshot of the upper atmosphere. The ones here were launched today around the Midwest."     
    follow_up_tweet = 'A few useful links on how to interpret soundings: http://www.wunderground.com/blog/24hourprof/introduction-to-skewt-logp-diagrams\nhttp://www.theweatherprediction.com/thermo/skewt/\nTo see more: http://weather.uwyo.edu/upperair/sounding.html'
    try:
        #print 'test'
        api.update_with_media(filename = 'soundingani.gif', status = tweet)
        api.update_status(status=follow_up_tweet) 
    except tweepy.error.TweepError:
        print ("Twitter error raised")
    plt.close('all') #closes all figures


# In[14]:

animate(GRB, MPX, DVN, ILX, api)

