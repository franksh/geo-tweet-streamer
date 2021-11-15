
"""
Run this script to start an interactive session with the Titter / Tweepy API
"""
import os
from IPython import embed
from geotweetlistener import GeoTweetListener

# Load config
try:
    # python 2.7
    from ConfigParser import ConfigParser
except:
    # python 3
    from configparser import ConfigParser
config = ConfigParser()

if os.path.isfile('config.mine.ini'):
    f = open('config.mine.ini')
else:
    f = open('config.ini')
config.readfp(f)
f.close()

# Import API Object
listener = GeoTweetListener(config=config, no_streaming=True)
api = listener.get_api()

embed()
