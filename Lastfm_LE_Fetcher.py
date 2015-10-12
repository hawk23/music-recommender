# Simple Last.fm API crawler to download listening events.
__author__ = 'mms'

# Load required modules
import os
import urllib
import csv
import json
import shutil


# Parameters
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY = "57ee3318536b23ee81d6b27e36997cde"                     # enter your API key
LASTFM_OUTPUT_FORMAT = "json"

MAX_PAGES = 5                           # maximum number of pages per user
MAX_ARTISTS = 50                        # maximum number of top artists to fetch
MAX_FANS = 10                           # maximum number of fans per artist
MAX_EVENTS_PER_PAGE = 200               # maximum number of listening events to retrieve per page

GET_NEW_USERS = False                    # set to True if new users should be retrieved
USERS_FILE = "./seed_users.csv"         # text file containing Last.fm user names

OUTPUT_DIRECTORY = "./"                 # directory to write output to
OUTPUT_FILE = "./users.txt"             # file to write output
LE_FILE = "./LE.txt"                    # aggregated listening events


# Simple function to read content of a text file into a list
def read_users(users_file):
    users = []                                      # list to hold user names
    with open(users_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')      # create reader
        for row in reader:
            users.append(row[0])
    return users


# Function to call Last.fm API: Users.getRecentTrack
def lastfm_api_call_getLEs(user, output_dir):
    content_merged = []        # empty list

    # Ensure that output directory structure exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Retrieve content from URL
    query_quoted = urllib.quote(user)
    # Loop over number of pages to retrieve
    for p in range(0, MAX_PAGES):
        # Construct API call
        url = LASTFM_API_URL + "?method=user.getrecenttracks&user=" + query_quoted + \
              "&format=" + LASTFM_OUTPUT_FORMAT + \
              "&api_key=" + LASTFM_API_KEY + \
              "&limit=" + str(MAX_EVENTS_PER_PAGE) + \
              "&page=" + str(p+1)

        print "Retrieving page #" + str(p+1)
        content = urllib.urlopen(url).read()

        # Add retrieved content of current page to merged content variable
        content_merged.append(content)

        # Write content to local file
        output_file = output_dir + "/" + user + "_" + str(p+1) + "." + LASTFM_OUTPUT_FORMAT
        file_out = open(output_file, 'w')
        file_out.write(content)
        file_out.close()

    # Return all content retrieved for given user
    return content_merged


# ADDED THIS NEW FUNCTION
# Function to call Last.fm API: Chart.getTopArtists
def lastfm_api_call_getTopArtists():
    content_merged = []        # empty list

    # Construct API call
    url = LASTFM_API_URL + "?method=chart.gettopartists" + \
          "&format=" + LASTFM_OUTPUT_FORMAT + \
          "&api_key=" + LASTFM_API_KEY + \
          "&limit=" + str(MAX_ARTISTS)

    content = urllib.urlopen(url).read()

    # Add retrieved content of current page to merged content variable
    content_merged.append(content)
    json_content = json.loads(content)

    artist_list = []

    for _artist in range(0, MAX_ARTISTS):
        artist_list.append((json_content["artists"]["artist"][_artist]["name"]).encode("utf-8"))

    # Write content to local file
    # output_file = "./topartist.txt"
    # file_out = open(output_file, 'w')
    # file_out.write(artist_list)
    # file_out.close()

    return artist_list


# ADDED THIS NEW FUNCTION
# Function to call Last.fm API: Artist.getTopFans
def lastfm_api_call_getTopFans(artist_list):
    content_merged = []        # empty list
    user_list = ""

    # Construct API call
    for _artist in range(0, MAX_ARTISTS):
        url = LASTFM_API_URL + "?method=artist.gettopfans" + \
          "&api_key=" + LASTFM_API_KEY + \
          "&artist=" + artist_list[_artist] + \
          "&format=" + LASTFM_OUTPUT_FORMAT

        _content = urllib.urlopen(url).read()

        # Add retrieved content of current page to merged content variable
        content_merged.append(_content)
        json_content = json.loads(_content)

        for _user in range(0, MAX_FANS):
            user_list += (json_content["topfans"]["user"][_user]["name"]).encode("utf-8") + '\n'

    # Write content to local file
    output_file = "./users.txt"
    file_out = open(output_file, 'w')
    file_out.write(artist_list)
    file_out.close()


# ADDED THIS NEW FUNCTION
# Function to call Last.fm API: Artist.getTopFans
def lastfm_api_call_getFriends(user):
    content_merged = []         # empty list
    friend_list = []            # empty list

    # Construct API call
    url = LASTFM_API_URL + "?method=user.getfriends" + \
        "&api_key=" + LASTFM_API_KEY + \
        "&user=" + str(user) + \
        "&format=" + LASTFM_OUTPUT_FORMAT

    _content = urllib.urlopen(url).read()

    # Add retrieved content of current page to merged content variable
    content_merged.append(_content)
    json_content = json.loads(_content)

    if "friends" in json_content.keys():
        for _friend in json_content["friends"]["user"]:
            friend_list.append(_friend["name"].encode("utf-8"))

    return friend_list


# Main program
if __name__ == '__main__':

    # Create output directory if non-existent
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

    # Read users from provided file
    users = read_users(USERS_FILE)
    user_list = users
    data = ""

    if (not os.path.exists(OUTPUT_FILE)) or GET_NEW_USERS:   # if you want to retrieve new users
        # Find friends from existing users to receive more than 500 users
        for _user in users:
            print "fetching friends of " + _user.encode("utf-8")
            user_list = lastfm_api_call_getFriends(_user)

            for u in user_list:
                data += u.encode("utf-8") + "\n"

            print "finished " + _user.encode("utf-8")

        if os.path.exists(OUTPUT_FILE):
            shutil.rmtree(OUTPUT_FILE)

        # Write content to local file
        file_out = open(OUTPUT_FILE, 'w')
        file_out.write(data)
        file_out.close()

        users = read_users(OUTPUT_FILE)
    else:
        users = read_users(OUTPUT_FILE)

    print "\n"

    # Create list to hold all listening events
    LEs = []

    # For all users, retrieve listening events
    for u in range(0, len(users)):
        print 'Fetching listening events for user #' + str(u+1) + ': ' + users[u] + ' ...'
        content = lastfm_api_call_getLEs(users[u], OUTPUT_DIRECTORY + "/listening_events/")

        # Parse retrieved JSON content
        try:
            # For all retrieved JSON pages of current user
            for page in range(0, len(content)):
                listening_events = json.loads(content[page])

                # Get number of listening events in current JSON
                no_items = len(listening_events["recenttracks"]["track"])

                # Read artist, track names and time stamp for each listening event
                for item in range(0, no_items):
                    artist = listening_events["recenttracks"]["track"][item]["artist"]["#text"]
                    track = listening_events["recenttracks"]["track"][item]["name"]
                    time = listening_events["recenttracks"]["track"][item]["date"]["uts"]
#                    print users[u], artist, track, time

                    # Add listening event to aggregated list of LEs
                    LEs.append([users[u], artist.encode('utf8'), track.encode('utf8'), str(time)])

        except KeyError:                    # JSON tag not found
            print "JSON tag not found!"
            continue

    # Write retrieved listening events to text file
    with open(LE_FILE, 'w') as outfile:             # "a" to append
        outfile.write('user\tartist\ttrack\ttime\n')
        for le in LEs:          # For all listening events
            outfile.write(le[0] + "\t" + le[1] + "\t" + le[2] + "\t" + le[3] + "\n")
