if __name__ == '__main__':
    """ Run this script to start the Streaming """
    import os

    # Load config
    try:
        # python 2.7
        from ConfigParser import ConfigParser
    except:
        # python 3
        from configparser import ConfigParser
    config = ConfigParser()

    from geotweetlistener import GeoTweetListener

    # Load private config file if exists, else standard config
    if os.path.isfile('config.mine.ini'):
        f = open('config.mine.ini')
    else:
        f = open('config.ini')
    config.readfp(f)
    f.close()

    # Create listener and start streaming
    listener = GeoTweetListener(config=config)
    listener.start_streaming()
