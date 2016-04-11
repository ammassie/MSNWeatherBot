
# coding: utf-8

# In[1]:

from siphon.catalog import TDSCatalog
import urllib2
from moviepy.editor import VideoFileClip
from netCDF4 import num2date
from metpy.io.gini import GiniFile
from metpy.plots.ctables import registry
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
from matplotlib import patheffects
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import tweepy
import random
#times are in UTC

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


# In[2]:

#Get imagery
def mapimagery():
    
    link = ['http://thredds.ucar.edu/thredds/catalog/satellite/WV/EAST-CONUS_4km/current/catalog.xml', 
             'http://thredds.ucar.edu/thredds/catalog/satellite/IR/EAST-CONUS_4km/current/catalog.xml',
             'http://thredds.ucar.edu/thredds/catalog/satellite/VIS/EAST-CONUS_1km/current/catalog.xml']
    keywords = ['WV', 'IR', 'Visible']
    descriptors = ['Water Vapor', 'Infrared', 'Visible']
    index = random.randint(0, len(link)-1) #random index that picks either wv, ir, or visible image to plot
    image = []
    for i in range(1,14,4): #loops through the first 4 hours, pulls out image from every hour
        fig = plt.figure(figsize = (10, 10))
        plt.subplots_adjust(hspace=0.03, wspace=0, top = 1, left = 0, right = 0.85, bottom = 0.0)
        plt.style.use('ggplot')
        plt.axis('off')
        figuretext ="""Satellite Imagery from GOES East Satellite (Imagery retrieved from UCAR/Unidata)
To explore more, check out the following links:
http://www.weather.gov/satellite               http://www.goes.noaa.gov/ 
http://www.ssec.wisc.edu/data/geo-new/#/animation
        
To learn how to interpret satellite imagery, check out the following links:
https://www.wunderground.com/about/satellite.asp 
http://www.weather.cod.edu/labs/satellitelab/satlab.ppt"""
        plt.figtext(0.05, 0.20, figuretext, horizontalalignment='left', verticalalignment='top',
                    fontsize = 16, color = 'white', bbox=dict(facecolor='gray', alpha = 0.85))
        
        cat = TDSCatalog(link[index]) ##current wv image
        dataset_name = sorted(cat.datasets.keys())[-i] #pulls the last one in the list above (most recent)
        dataset = cat.datasets[dataset_name] #saves that file into a dataset object
        remote_gini_file = urllib2.urlopen(dataset.access_urls['HTTPServer'])
        gini = GiniFile(remote_gini_file) ## MetPy's built in function to read gini files and parse them for you
        gini_ds = gini.to_dataset() ## converts to more comprehensive dataset
        x = gini_ds.variables['x'][:]
        y = gini_ds.variables['y'][:]
        dat = gini_ds.variables[str(keywords[index])]
            
        proj_var = gini_ds.variables[dat.grid_mapping] #pulls out the grid information (projection)
        #print(proj_var)
        
        # Create CartoPy projection information for the file
        globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.earth_radius,
                            semiminor_axis=proj_var.earth_radius)

        proj = ccrs.LambertConformal(central_longitude=proj_var.longitude_of_central_meridian,
                                     central_latitude=proj_var.latitude_of_projection_origin,
                                     standard_parallels=[proj_var.standard_parallel], globe=globe)
        
        # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
        states_provinces = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none')

        lakes = cfeature.NaturalEarthFeature(
            category='physical',
            name='lakes',
            scale='110m',
            facecolor='none')

        ax = fig.add_subplot(1,1,1, projection=proj)
        ax.add_feature(states_provinces, edgecolor='black', linewidth=2.0) 
        ax.add_feature(lakes, edgecolor='black', linewidth=2.0) 
        ax.coastlines(resolution='50m', zorder=2, color='black', linewidth=2.0)
        ax.add_feature(cfeature.BORDERS, linewidth=2.0) #find way to make higher res
            
        if 'WV' in link[index]: #for wv color
            map_norm, map_cmap = registry.get_with_steps('WVCIMSS', 0, 1) #color ramp
            im = ax.imshow(dat[:], cmap=map_cmap, norm=map_norm, zorder=0,
                           extent=(x.min(), x.max(), y.min(), y.max()), origin='upper')
        else: #for vis/ir color
            im = ax.imshow(dat[:], extent=(x.min(), x.max(), y.min(), y.max()), origin='upper',
                           cmap='gray', norm=plt.Normalize(0, 255)) 

        time_var = gini_ds.variables['time']
        timestamp = num2date(time_var[:].squeeze(), time_var.units)

        text = ax.text(0.99, 0.95, timestamp.strftime('%d %B %Y %H%MZ'),
                       horizontalalignment='right', transform=ax.transAxes,
                       color='white', fontsize=20, weight='bold')
        title = descriptors[index] + ' Satellite Image' 
        title_text = ax.text(0.99, 0.9, title, horizontalalignment='right', transform=ax.transAxes,
                             color='white', fontsize=20, weight='bold')
        title_text.set_path_effects([patheffects.Stroke(linewidth=2, foreground='black'), patheffects.Normal()])
        text.set_path_effects([patheffects.Stroke(linewidth=2, foreground='black'), patheffects.Normal()])
        fig.tight_layout()
        #plt.show()
        plt.savefig('Satellite_Figure_' + str(i) + '.png', bbox_inches='tight', pad_inches=0)
        image.append('Satellite_Figure_' + str(i) + '.png')
        plt.close()
    return image


# In[3]:

def animate(pics): #animate and tweet
    image = []
    for i in range(len(pics)-1, -1, -1): #reverses images so that they're in the correct order in the loop
        image.append(pics[i])
    
    fig = plt.figure(figsize = (20,20))
    def func(image):
        img = mpimg.imread(image)
        line = plt.imshow(img)
        return line

    mywriter = animation.FFMpegWriter(fps=2)
    ax = plt.axes()
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ani = animation.FuncAnimation(fig, func, image, interval = 1000)
    fig.tight_layout()
    ani.save('SatImage.mp4',writer=mywriter)
    filename = 'SatImage.gif'
    clip = (VideoFileClip("SatImage.mp4"))
    clip.write_gif("SatImage.gif")
    plt.close('all')
    return filename


# In[4]:

def sat_tweet(api):
    pics = mapimagery()
    gif_file = animate(pics) #four hour loop, four image files
    tweet = "How GOES it? Here's the latest from space. Explore more here: http://www.ssec.wisc.edu/data/geo-new/#/animation"
    
    try: #first, attempt a 4 hour tweet
        api.update_with_media(filename = gif_file, status = tweet)
        print 'Tweet successful! check SatImage.gif'
    except tweepy.error.TweepError:
        print("Twitter error raised, file is probably too big, try again with one less image")
        del pics[-1]
        new_gif_file = animate(pics) #recreates animation, with one less image file
        
        #Try again
        try:
            api.update_with_media(filename = new_gif_file, status = tweet)
            print 'Tweet successful! check SatImage.gif'
        except tweepy.error.TweepError:
            print("Twitter error raised, file is still probably too big")
            
            #stop trying to animate, just use a static image
            try:
                api.update_with_media(filename = 'Satellite_Figure_1.png', status = tweet)
                print 'Tweet successful!'
            except tweepy.error.TweepError:
                print("Twitter error raised")


# In[5]:

sat_tweet(api)

