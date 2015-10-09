import urllib
import os
import csv
import json


OUTPUT_DIR = "./user_info/"
USER_FILE = "./seed_users.csv"

LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY = ""                     # enter your API key

# Read input file of user names
def read_user_file(uf):
    users = []       # init list
    with open(uf, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for r in reader:
            users.append(r[0])
    return users

# Call Last.fm API to gather user information
def lfm_api_call_getinfo(user):
    url = LASTFM_API_URL + "?method=user.getinfo&user=" + urllib.quote(user) + \
          "&format=json" + "&api_key=" + LASTFM_API_KEY
    content = urllib.urlopen(url).read()
    return content


# Main program
if __name__ == '__main__':
    # Ensure that output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Read list of seed users
    users = read_user_file(USER_FILE)

    # Call Last.fm API: user.getInfo for all seed users
    for u in users:
        c = lfm_api_call_getinfo(u)

        # Write output
        output_file = OUTPUT_DIR + "/" + u + '.json'
        fh = open(output_file, 'w')
        fh.write(c)
        fh.close()

        # Parse json
        user_data = json.loads(c)
        print user_data
        print user_data["user"]["name"]
        print user_data["user"]["playcount"]
        print user_data["user"]["registered"]["unixtime"]
