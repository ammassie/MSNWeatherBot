
# coding: utf-8

# In[26]:

import urllib2, zipfile, os
from datetime import datetime
import datetime as dat
from os import listdir
import matplotlib.pyplot as plt
from cartopy import crs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.feature as cfeature
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
import matplotlib.animation as animation
from moviepy.editor import VideoFileClip
import tweepy

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


# In[27]:

def getDateTime():
    date = str(datetime.utcnow())
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = date[11:13]
    return date, year, month, day, hour


# In[28]:

def getSPCfiles():
    date, year, month, day, hour = getDateTime()
    #get URLS, subtract 1 hour once daylight savings time starts
    #day = '31' #for if you're working on this and it's past 6Z
    #month = '05'
    #year = '2013'
    day1url = "http://www.spc.noaa.gov/products/outlook/archive/" + str(year) + "/day1otlk_" + str(year) + str(month) + str(day) + "_1300-shp.zip"
    day2url = "http://www.spc.noaa.gov/products/outlook/archive/" + str(year) + "/day2otlk_" + str(year) + str(month) + str(day) + "_0600-shp.zip"
    day3url = "http://www.spc.noaa.gov/products/outlook/archive/" + str(year) + "/day3otlk_" + str(year) + str(month) + str(day) + "_0730-shp.zip"
    day4url = "http://www.spc.noaa.gov/products/exper/day4-8/day4prob-shp.zip"
    day5url = "http://www.spc.noaa.gov/products/exper/day4-8/day5prob-shp.zip"
    day6url = "http://www.spc.noaa.gov/products/exper/day4-8/day6prob-shp.zip"
    day7url = "http://www.spc.noaa.gov/products/exper/day4-8/day7prob-shp.zip"
    day8url = "http://www.spc.noaa.gov/products/exper/day4-8/day8prob-shp.zip"
    urlList = [day1url, day2url, day3url, day4url, day5url, day6url, day7url, day8url]
    
    #download files
    for i in range(len(urlList)):
        link = urllib2.urlopen(urlList[i])
        spcfile = link.read()
        with open("SPC_CO.zip", "wb") as f:
            f.write(spcfile)
            f.close()
        with zipfile.ZipFile('SPC_CO.zip', "r") as z:
            z.extractall()
            z.close()
    #print urlList


# In[29]:

def catfiles(): #gets categorical outlooks
    cat = []
    directory = listdir('.') #lists spc files in current directory
    
    for i in range(len(directory)):
        if 'day1' in directory[i] and directory[i].endswith('.shp'):
            if directory[i].endswith('cat.shp'):
                cat.append(directory[i])
        elif 'day2' in directory[i] and directory[i].endswith('cat.shp'):
            cat.append(directory[i])
        elif 'day3' in directory[i] and directory[i].endswith('cat.shp'):
            cat.append(directory[i])
    return cat


# In[30]:

def windfiles(): #gets day 1 wind prob files
    wind = []
    directory = listdir('.') #lists spc files in current directory
    
    for i in range(len(directory)):
        if 'wind.shp' in directory[i]:
            wind.append(directory[i])
    #print sorted(wind, reverse = True)
    return sorted(wind, reverse = True)


# In[31]:

def hailfiles(): #gets day 1 hail prob files
    hail = []
    directory = listdir('.') #lists spc files in current directory
    
    for i in range(len(directory)):
        if 'hail.shp' in directory[i]:
            hail.append(directory[i])
    #print sorted(hail)
    return sorted(hail)


# In[32]:

def tornfiles(): #gets day 1 torn prob files
    torn = []
    directory = listdir('.') #lists spc files in current directory
    
    for i in range(len(directory)):
        if 'torn.shp' in directory[i]:
            torn.append(directory[i])
    #print 'Torn files'
    #print sorted(torn, reverse = True)
    return sorted(torn, reverse = True)


# In[33]:

def day4_8files(): #gets day 4-8 prob files
    day4_8 = []
    directory = listdir('.') #lists spc files in current directory
    
    for i in range(len(directory)):
        if directory[i].endswith('prob.shp'):
            if 'day1' in directory[i]:
                continue
            elif 'day2' in directory[i]:
                continue
            elif 'day3' in directory[i]:
                continue
            else:
                day4_8.append(directory[i])
                
    return day4_8


# In[34]:

def makeCatPlots(): #makes day 1-3 convective outlooks
    cat = catfiles() #list of files
    SPCimagefiles = [] #list of image files
    valid = [] #valid time
    expire = [] #expire time
    
    for i in range(len(cat)):
        plt.figure()
        xmin = -120
        xmax = -70
        ymin = 20
        ymax = 55
        ax = plt.axes(projection=crs.LambertConformal())
        ax.add_feature(cfeature.OCEAN, edgecolor = 'gray', linewidth = 1.5)
        ax.add_feature(cfeature.LAKES)
        ax.add_feature(ShapelyFeature(Reader("ne_50m_admin_1_states_provinces_lakes.shp").geometries(), crs.PlateCarree(), facecolor = 'w', edgecolor = 'gray', linewidth=1.5))
        ax.set_extent([xmin, xmax, ymin, ymax])
        
        shpfile = cat[i] #plotted shapefile
        dn = Reader(shpfile).records()

        for j in dn:
            if j.attributes['VALID'] not in valid:
                valid.append(j.attributes['VALID'])
            if j.attributes['EXPIRE'] not in expire:
                expire.append(j.attributes['EXPIRE'])
            #plots each category    
            if j.attributes['DN'] == 2:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='lightgreen', alpha=.75)
            elif j.attributes['DN'] == 3:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='green', alpha=.75)
            elif j.attributes['DN'] == 4:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='yellow', alpha=.75)
            elif j.attributes['DN'] == 5:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='orange', alpha=.75) 
            elif j.attributes['DN'] == 6:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='red', alpha=.75) 
            elif j.attributes['DN'] == 7:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='fuchsia', alpha=.75) 
        #start of text for blurb at bottom
        start = valid[i]
        validyear = start[0:4]
        validmonth = start[4:6]
        validday = start[6:8]
        validhour = start[8:12]

        end = expire[i]
        expireyear = end[0:4]
        expiremonth = end[4:6]
        expireday = end[6:8]
        expirehour = end[8:12]

        plt.title('SPC Convective Outlook: Day ' + str(i+1))
        filename = 'SPCDay' + str(i+1) + '.png'
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        #makes key
        tstm = mpatches.Patch(color='lightgreen', label='TSTM')
        mrgl = mpatches.Patch(color='green', label='MRGL')
        slgt = mpatches.Patch(color='yellow', label='SLGT')
        enh = mpatches.Patch(color='orange', label='ENH')
        mdt = mpatches.Patch(color='red', label='MDT')
        high = mpatches.Patch(color='fuchsia', label='HIGH')
        
        plt.legend(handles=[tstm, mrgl, slgt, enh, mdt, high], loc='lower right', fontsize = '8')
        text = 'Valid: ' + validmonth + '/' + validday + '/' + validyear + ' ' + validhour + 'Z - ' + expiremonth + '/' + expireday + '/' + expireyear + ' ' + expirehour + 'Z\nData from NWS/NOAA Storm Prediction Center (www.spc.noaa.gov)\nFind discussions about these categories on the SPC website.'
        ax.text(0.01, 0.01, text, verticalalignment = 'bottom', horizontalalignment = 'left', transform=ax.transAxes, fontsize = '8', bbox=dict(facecolor='white', alpha=0.75))
        plt.savefig(filename, bbox_inches='tight')
        SPCimagefiles.append(filename)
        plt.close()
        ### end of categorical convective outlooks
    print "Successfully made the following maps: "
    print SPCimagefiles


# In[35]:

def day4_8Plots(): #plots day 4-8 severe weather risk
    day4_8 = day4_8files() #list of files
    SPCimagefiles = [] #list of image files
    risklevel = [] #for day 4-8
    Day4_8Risk = False #for if there's warnings in day 4-8 (set to no warnings as of now)
    for i in range(len(day4_8)):
        shpfile = day4_8[i]
        dn = Reader(shpfile).records()
        for j in dn:
            risklevel.append(j.attributes['DN']) #pulls out the risk number
    
    for i in range(len(day4_8)):
        if risklevel[i] != 0: 
            Day4_8Risk = True # there is a warning on day 4-8, want to plot them all individually
            print 'Day4-8 Risk is True'
            break
        
    if Day4_8Risk == False: #if there's no risk for day 4-8
        plt.figure()
        xmin = -120
        xmax = -70
        ymin = 20
        ymax = 55
        start = str(datetime.utcnow() + dat.timedelta(days=3)) #for the valid/expire time
        validyear = start[0:4]
        validmonth = start[5:7]
        validday = start[8:10]
        validhour = str(1200)

        end = str(datetime.utcnow() + dat.timedelta(days=8))
        expireyear = end[0:4]
        expiremonth = end[5:7]
        expireday = end[8:10]
        expirehour = str(1200)
        
        ax = plt.axes(projection=crs.LambertConformal())
        ax.add_feature(cfeature.OCEAN, edgecolor = 'gray', linewidth = 1.5)
        ax.add_feature(cfeature.LAKES)
        ax.add_feature(ShapelyFeature(Reader("ne_50m_admin_1_states_provinces_lakes.shp").geometries(), crs.PlateCarree(), facecolor = 'w', edgecolor = 'gray', linewidth=1.5))
        ax.set_extent([xmin, xmax, ymin, ymax])
        plt.title('SPC Convective Outlook Day 4-8: Low Probability/Predictability')
        filename = 'SPCDay4-8.png'
        text = 'Valid: ' + validmonth + '/' + validday + '/' + validyear + ' ' + validhour + 'Z - ' + expiremonth + '/' + expireday + '/' + expireyear + ' ' + expirehour + 'Z\nPredictability or potential for severe weather too low\nData from NWS/NOAA Storm Prediction Center (www.spc.noaa.gov)\nFind discussions about these categories on the SPC website.'
        ax.text(0.01, 0.01, text, verticalalignment = 'bottom', horizontalalignment = 'left', transform=ax.transAxes, fontsize = '8', bbox=dict(facecolor='white', alpha=0.75))
 
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)

        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        SPCimagefiles.append(filename)    
    else: #if there is any risk on any of days 4-8
        valid = [] #outlook valid time
        expire = [] #outlook expire time
        for i in range(len(day4_8)):
            plt.figure()
            xmin = -120
            xmax = -70
            ymin = 20
            ymax = 55
            ax = plt.axes(projection=crs.LambertConformal())
            ax.add_feature(cfeature.OCEAN, edgecolor = 'gray', linewidth = 1.5)
            ax.add_feature(cfeature.LAKES)
            ax.add_feature(ShapelyFeature(Reader("ne_50m_admin_1_states_provinces_lakes.shp").geometries(), crs.PlateCarree(), facecolor = 'w', edgecolor = 'gray', linewidth=1.5))
            ax.set_extent([xmin, xmax, ymin, ymax])

            shpfile = day4_8[i]
            dn = Reader(shpfile).records()

            for j in dn:
                if j.attributes['VALID'] not in valid:
                    valid.append(j.attributes['VALID'])
                if j.attributes['EXPIRE'] not in expire:
                    expire.append(j.attributes['EXPIRE'])
                if j.attributes['DN'] == 15:
                    ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='yellow', alpha=.75)
                elif j.attributes['DN'] == 30:
                    ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='orange', alpha=.75)
            plt.title('SPC Convective Outlook: Day ' + str(i+4))
            filename = 'SPCDay' + str(i+4) + '.png'
            #for blurb at bottom, with valid/expiration times

            start = valid[i]
            validyear = start[0:4]
            validmonth = start[4:6]
            validday = start[6:8]
            validhour = start[8:12]

            end = expire[i]
            expireyear = end[0:4]
            expiremonth = end[4:6]
            expireday = end[6:8]
            expirehour = end[8:12]

            ax.yaxis.set_visible(False)
            ax.xaxis.set_visible(False)
            text = 'Valid: ' + validmonth + '/' + validday + '/' + validyear + ' ' + validhour + 'Z - ' + expiremonth + '/' + expireday + '/' + expireyear + ' ' + expirehour + 'Z\nData from NWS/NOAA Storm Prediction Center (www.spc.noaa.gov)\nFind discussions about these categories on the SPC website.'
            ax.text(0.01, 0.01, text, verticalalignment = 'bottom', horizontalalignment = 'left', transform=ax.transAxes, fontsize = '8', bbox=dict(facecolor='white', alpha=0.75))
            #for the legend on the right
            fifteen = mpatches.Patch(color='yellow', label='15%')
            thirty = mpatches.Patch(color='orange', label='30%') 
            plt.legend(handles=[thirty, fifteen], loc='lower right', fontsize = '8') 
            plt.savefig(filename, bbox_inches='tight')
            plt.close()
            SPCimagefiles.append(filename)
    
    print "Successfully made the following maps: "
    print SPCimagefiles
    


# In[36]:

def tornadoPlot(): #plots tornado outlook
    torn = tornfiles()
    SPCimagefiles = []
    valid = []
    expire = []
    plt.figure(1)
    
    xmin = -120
    xmax = -70
    ymin = 20
    ymax = 55
    ax = plt.axes(projection=crs.LambertConformal())
    ax.add_feature(cfeature.OCEAN, edgecolor = 'gray', linewidth = 1.5)
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(ShapelyFeature(Reader("ne_50m_admin_1_states_provinces_lakes.shp").geometries(), crs.PlateCarree(), facecolor = 'w', edgecolor = 'gray', linewidth=1.5))
    ax.set_extent([xmin, xmax, ymin, ymax])
    plt.title('SPC Day 1: Tornado Outlook') 
    filename = 'SPCDay1Tornado.png'
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)

    two = mpatches.Patch(color='green', label='2%')
    five = mpatches.Patch(color='brown', label='5%')
    ten = mpatches.Patch(color='yellow', label='10%')
    fifteen = mpatches.Patch(color='red', label='15%')
    thirty = mpatches.Patch(color='fuchsia', label='30%')
    fourtyfive = mpatches.Patch(color='purple', label='45%')
    sixty = mpatches.Patch(color='blue', label='60%')
    sig = mpatches.Patch(color='k', label='Sig')
    plt.legend(handles=[two, five, ten, fifteen, thirty, fourtyfive, sixty, sig], loc='lower right', fontsize = '8')

    for i in range(len(torn)):
        shpfile = torn[i]
        dn = Reader(shpfile).records()
    
        for j in dn:
            valid.append(j.attributes['VALID'])
            expire.append(j.attributes['EXPIRE'])
            
            if j.attributes['DN'] == 2:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='green', alpha=.75)
            elif j.attributes['DN'] == 5:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='brown', alpha=.75)
            elif j.attributes['DN'] == 15:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='red', alpha=.75)
            elif j.attributes['DN'] == 30:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='fuchsia', alpha=.75)
            elif j.attributes['DN'] == 45:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='purple', alpha=.75)
            elif j.attributes['DN'] == 60:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='blue', alpha=.75)
                
            if 'sigtorn.shp' in shpfile:
                if j.attributes['DN'] == 10:
                    ax.add_geometries(j.geometry, 
                                      crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), 
                                      facecolor = 'none', hatch = '////')  
            else:
                if j.attributes['DN'] == 10:
                    ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='yellow')

    #start of text for blurb at bottom
    start = valid[0]
    validyear = start[0:4]
    validmonth = start[4:6]
    validday = start[6:8]
    validhour = start[8:12]

    end = expire[0]
    expireyear = end[0:4]
    expiremonth = end[4:6]
    expireday = end[6:8]
    expirehour = end[8:12]

    text = 'Valid: ' + validmonth + '/' + validday + '/' + validyear + ' ' + validhour + 'Z - ' + expiremonth + '/' + expireday + '/' + expireyear + ' ' + expirehour + 'Z\nData from NWS/NOAA Storm Prediction Center (www.spc.noaa.gov)\nFind discussions about these categories on the SPC website.'
    ax.text(0.01, 0.01, text, verticalalignment = 'bottom', horizontalalignment = 'left', transform=ax.transAxes, fontsize = '8', bbox=dict(facecolor='white', alpha=0.75))
    
    
    plt.savefig(filename, bbox_inches='tight', fontsize = '8')    
    SPCimagefiles.append(filename) 
    print "Successfully made the following maps: "
    print SPCimagefiles
    plt.close()


# In[37]:

def windhailPlot(files, name): #plots day 1 wind & hail probability
    SPCimagefiles = []
    valid = []
    expire = []
    
    plt.figure()
    xmin = -120
    xmax = -70
    ymin = 20
    ymax = 55
        
    ax = plt.axes(projection=crs.LambertConformal())
    ax.add_feature(cfeature.OCEAN, edgecolor = 'gray', linewidth = 1.5)
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(ShapelyFeature(Reader("ne_50m_admin_1_states_provinces_lakes.shp").geometries(), crs.PlateCarree(), facecolor = 'w', edgecolor = 'gray', linewidth=1.5))
    ax.set_extent([xmin, xmax, ymin, ymax])
    plt.title('SPC Day 1: ' + name + ' Outlook') 
    filename = 'SPCDay1' + name + '.png'
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)

    five = mpatches.Patch(color='brown', label='5%')
    fifteen = mpatches.Patch(color='yellow', label='15%')
    thirty = mpatches.Patch(color='red', label='30%')
    fourtyfive = mpatches.Patch(color='fuchsia', label='45%')
    sixty = mpatches.Patch(color='purple', label='60%')
    sig = mpatches.Patch(color='k', label='Sig')
    plt.legend(handles=[five, fifteen, thirty, fourtyfive, sixty, sig], loc='lower right', fontsize = '8')

    for i in range(len(files)):
        shpfile = files[i]
        dn = Reader(shpfile).records()
        for j in dn:
            if j.attributes['VALID'] not in valid:
                valid.append(j.attributes['VALID'])
            if j.attributes['EXPIRE'] not in expire:
                expire.append(j.attributes['EXPIRE'])
                
            if j.attributes['DN'] == 5:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='brown', alpha=.75)
            elif j.attributes['DN'] == 15:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='yellow', alpha=.75)
            elif j.attributes['DN'] == 30:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='red', alpha=.75)
            elif j.attributes['DN'] == 45:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='fuchsia', alpha=.75)
            elif j.attributes['DN'] == 60:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0), facecolor='purple', alpha=.75)
            elif j.attributes['DN'] == 10:
                ax.add_geometries(j.geometry, crs.LambertConformal(central_longitude = 0.0, central_latitude=0.0),                                   facecolor = 'none', hatch = '/////', alpha=.75) 
    
    #start of text for blurb at bottom
    start = valid[0]
    validyear = start[0:4]
    validmonth = start[4:6]
    validday = start[6:8]
    validhour = start[8:12]

    end = expire[0]
    expireyear = end[0:4]
    expiremonth = end[4:6]
    expireday = end[6:8]
    expirehour = end[8:12]
    
    text = 'Valid: ' + validmonth + '/' + validday + '/' + validyear + ' ' + validhour + 'Z - ' + expiremonth + '/' + expireday + '/' + expireyear + ' ' + expirehour + 'Z\nData from NWS/NOAA Storm Prediction Center (www.spc.noaa.gov)\nFind discussions about these categories on the SPC website.'
    ax.text(0.01, 0.01, text, verticalalignment = 'bottom', horizontalalignment = 'left', transform=ax.transAxes, fontsize = '8', bbox=dict(facecolor='white', alpha=0.75))
    
    plt.savefig(filename, bbox_inches='tight', fontsize = '8')
    SPCimagefiles.append(filename) 
    print "Successfully made the following maps: "
    print SPCimagefiles
    plt.close()


# In[38]:

def deleteFiles():
    fnames = listdir('.') #lists everything in the current directory
    count = 0 #number of files for deletion
    filesfordel = []
    for i in range (len(fnames)):
        if 'otlk' in fnames[i]: #search for shape file name (could be day1, 2, 3 etc)
            filesfordel.append(fnames[i])
        if 'SPC' in fnames[i] and '.png' in fnames[i]: #search for SPC images
            filesfordel.append(fnames[i])
    for i in filesfordel:
        os.remove(i)
        count = count + 1

    print "Successfully deleted " + str(count) + " files."


# In[39]:

def animate(): #makes a gif
    fnames = listdir('.')
    image = []

    for i in range (len(fnames)):
        if 'SPC' in fnames[i] and '.png' in fnames[i]: #search for a file name (could be day1, 2, 3 etc)
            image.append(fnames[i])

    fig = plt.figure()
    def func(image):
        img = mpimg.imread(image)
        line = plt.imshow(img)
        return line

    mywriter = animation.FFMpegWriter(fps=0.5)
    ax = plt.axes()
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ani = animation.FuncAnimation(fig, func, image, interval = 1000)
    fig.tight_layout()
    ani.save('SPCani.mp4',writer=mywriter)
    clip = (VideoFileClip("SPCani.mp4"))
    clip.write_gif("SPCani.gif")
    plt.close()


# In[40]:

def SPCtweet(api):
    getSPCfiles()
    makeCatPlots()
    day4_8Plots()
    tornadoPlot()
    windhailPlot(windfiles(), 'Wind')
    windhailPlot(hailfiles(), 'Hail')
    animate()
    tweet = 'Where is the biggest threat for severe weather in the next few days? Learn more here: http://www.spc.noaa.gov/'
    try:
        #print 'check spcani.gif'
        api.update_with_media(filename = 'SPCani.gif', status = tweet)
    except tweepy.error.TweepError:
        print("Twitter error raised")
    deleteFiles()
    plt.close('all')


# In[ ]:

SPCtweet(api)

