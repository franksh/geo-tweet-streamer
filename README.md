# Geolocated Tweets Streaming Client

A simple Python3 client that saves all geolocated Tweets
with their coordinates in a given geographic region.

## Install

Clone the repository.

```shell
git clone https://github.com/franksh/geo-tweet-streamer.git
```

Then install the required libraries.

```shell
pip install -r requirements.txt
```


## Usage

Before you use the script, make sure that the ```config.ini```
is set up correctly (see Configuration below).

To start streaming, execute the script ```start_geotweet_listening.py```.
The script will start listening to the Twitter API.
It will save all geolocated Tweets in
the specified geographic region the format:

| created_at | user_id | tweet_id | latitude | longitude |

Tweets will be saved in a csv file or in a MySQL Database.

*Note:* Avoid starting and stopping the script repeatedly. The Twitter API
has a rate limit, and if you make too many connections in a short time
you might have to wait for a cooldown period to connect again.


### Streaming in the background

If you want the process to keep running in the background,
first make sure that the script is executable:

```shell
chmod +x start_geotweet_listening.py
```

Then start the process using ```nohup``` to keep it running
if you close the tab:

```shell
nohup python3 start_geotweet_listening.py &
```

To stop the process at a later time, use

```shell
ps ax | grep start_geotweet_listening.py
```

to find the process ID and kill it with

```shell
kill {PID}
```

## Configuration

The ```config.ini``` in the main directory contains the configuration of the
client.

### Twitter API Authentication

You need authentication tokens for the Twitter API
and enter them in the config.
See the [Twitter API Docs on authentication](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens)
on how to obtain these tokens.

### Data storage

The client supports saving the data either in a **csv** file or
in a **MySQL** database.

If you want to use MySQL, you have to specify the user, password and database
in the config. If the database doesn't exist yet it will be created.

### Geographic region

The script will save all tweets within a geographic bounding box. The bounding
box is specified in the config by minimal/maximal latitude and longitude.
