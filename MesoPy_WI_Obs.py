
# coding: utf-8

# In[1]:

from MesoPy import Meso
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
import tweepy


# In[2]:

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


# In[3]:

def surfacePlot(api):
    m = Meso(token=MesoPy_token)
    stids = ['KAIG', 'KATW', 'KASX', 'KDLL', 'KOVS', 'KBUU', 'KCLI', 'KEGV', 'KEAU', 'KFLD',
            'KCMY', 'KGRB', 'KHYR', 'KJVL', 'KUNU', 'KENW', 'KLSE', 'KRCX', 'KLNL', 'KLNR',
            'KMSN', 'KMTW', 'KMFI', 'KMDZ', 'KLUM', 'KRRL', 'KMKE', 'KMRJ', 'K82C', 'TT278',
            'KEFT', 'KRNH', 'KOSH', 'KPBH', 'KPVB', 'KPDC', 'KRHI', 'KBCK', 'LAAW3', 'WUEW3',
            'KRPD', 'KEZS', 'KSBM', 'KRZN', 'KSTE', 'KSUE', 'KSUW', 'KY51', 'KRYV', 'KUES',
            'KPCZ', 'KAUW', 'KY50', 'KETB', 'KISW', 'KARV', 'GDNW3', 'KRGK', 'AFWW3'] #stations
    latest = m.latest(stid=stids, within='30', vars='air_temp', units='temp|F') #gets the latest temps (measured over past 30 minutes)
    data = [] #a list with 4 columns: lat, long, temps, stid
    for ob in latest['STATION']:
        data.append((float(ob['LATITUDE']), float(ob['LONGITUDE']),
                     float(ob['OBSERVATIONS']['air_temp_value_1']['value']),ob['STID'])) 
    # Now that we have all the data, we can make the figure
    fig = plt.figure(figsize=(10,10))
    plt.style.use('ggplot')
    ax = plt.axes(projection=ccrs.Mercator())
    ax.set_extent([-86.5, -93.2, 41.75, 47.25])
    ax.add_feature(ShapelyFeature(Reader("ne_50m_admin_1_states_provinces_lakes.shp").geometries(), 
                                  ccrs.PlateCarree(), facecolor = 'w', edgecolor = 'gray', linewidth=1.5))
    county_shpfile = 'c_05ap16.shp' #wi county shapefile
    WI = Reader(county_shpfile).records()
    for i in WI:
        if i.attributes['STATE'] == 'WI':
            ax.add_geometries(i.geometry, ccrs.PlateCarree(), facecolor='white',edgecolor = 'gray')
    
    roads = cfeature.NaturalEarthFeature(
        category='cultural',
        name='roads',
        scale='10m',
        facecolor = 'none')
    ax.add_feature(roads, edgecolor='red')
    ax.add_feature(ShapelyFeature(Reader("ne_50m_lakes.shp").geometries(),
                                  ccrs.PlateCarree(), facecolor = 'lightblue', edgecolor = 'gray', linewidth=1.5))
    
    for lat, lon, temp, stid in data: #plots a marker for each station
        plt.plot(lon, lat, marker='o', color='blue', markersize=10,
                 alpha=0.7, transform = ccrs.PlateCarree()) 

    # Transforms for the text function
    transform = ccrs.PlateCarree()._as_mpl_transform(ax)
    text_transform = offset_copy(transform, units='dots', x=0, y=0)

    # Plot temp for each of the markers
    for lat, lon, temp, stid in data:
        plt.text(lon, lat, str(round(temp, 1)) + u'\N{DEGREE SIGN}' + 'F\n\n',
                 verticalalignment='center', horizontalalignment='center',
                 transform=text_transform, fontsize=11)
    
    uppertext = """Surface Observations 
over Wisconsin, taken
in the last 30 minutes.
Data accessed from
MesoWest and 
SynopticLabs.\n"""

    lowertext = """See more current surface observations here: 
http://mesowest.utah.edu/
http://aos.wisc.edu/weather/wx_obs/Surface.html
Learn how to interpret surface observation symbols here: 
http://ww2010.atmos.uiuc.edu/%28Gh%29/guides/maps/sfcobs/home.rxml"""
    ax.text(0.015, 0.01, lowertext, verticalalignment = 'bottom', horizontalalignment = 'left', 
            transform=ax.transAxes, fontsize = '10.5', bbox=dict(facecolor='white', alpha = 0.5))
    ax.text(0.015, 0.13, uppertext, verticalalignment = 'bottom', horizontalalignment = 'left', 
            transform=ax.transAxes, fontsize = '10.5', bbox=dict(facecolor='white', alpha = 0.5))
    plt.title('Current Weather Around Wisconsin', fontsize=14)
    plt.savefig('WI_Obs.png', bbox_inches = 'tight')
    #plt.show()
    
    tweet = "What's the weather like around WI? Find out more here: http://aos.wisc.edu/weather/wx_obs/Surface.html"
    try:
        #print 'WI_Obs.png'
        api.update_with_media("WI_Obs.png", status = tweet)
    except tweepy.error.TweepError:
        print ("Twitter error raised")
    plt.close('all')


# In[4]:

surfacePlot(api)

