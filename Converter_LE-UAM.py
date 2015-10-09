# Converts crawled listening events data from Last.fm to user-artist-matrix
__author__ = 'mms'

# Load required modules
import csv
import numpy as np

# Parameters
LE_FILE = "LE.txt"                      # aggregated listening events, to read from
UAM_FILE = "UAM.txt"                    # user-artist-matrix (UAM)
ARTISTS_FILE = "UAM_artists.txt"        # artist names for UAM
USERS_FILE = "UAM_users.txt"            # user names for UAM


# Main program
if __name__ == '__main__':

    artists = {}            # dictionary used as ordered list of artists without duplicates
    users = {}              # dictionary used as ordered list of users without duplicates
    listening_events = {}   # dictionary to store assignments between users and artists, i.e. (user, artist) tuples

    # Read listening events from provided file and initialize data structures
    with open(LE_FILE, 'r') as f:
        reader = csv.reader(f, delimiter='\t')      # create reader
        headers = reader.next()                     # skip header
        for row in reader:
            user = row[0]
            artist = row[1]
            track = row[2]
            time = row[3]

            # Create ordered set (list) of unique elements (for artists / tracks)
            artists[artist] = None
            users[user] = None

            # Initialize listening event counter, access by tuple (user, artist) in dictionary
            listening_events[(user, artist)] = 0

    # Read listening events from provided file and fill user-artist matrix
    with open(LE_FILE, 'r') as f:
        reader = csv.reader(f, delimiter='\t')      # create reader
        headers = reader.next()                     # skip header
        for row in reader:
            user = row[0]
            artist = row[1]
            track = row[2]
            time = row[3]
            # Increase listening counter for (user, artist) pair/tuple
            listening_events[(user, artist)] += 1


    # Assign a unique index to all artists and users in dictionary (we need these to create the UAM)
    # Artists
    counter = 0
    for artist in artists.keys():
        artists[artist] = counter
        counter += 1
    # Users
    counter = 0
    for user in users.keys():
        users[user] = counter
        counter += 1

    # Now we use numpy to create the UAM
    UAM = np.zeros(shape=(len(users.keys()), len(artists.keys())), dtype=np.float32)    # create an empty matrix of size |users| * |artists|
    # Iterate through all (user, artist) tuples in listening events
    for u in users.keys():
        for a in artists.keys():
            try:
                # Get correct index for user u and artist a
                idx_u = users[u]
                idx_a = artists[a]

                # Insert number of listening events of user u to artist a in UAM
                UAM[idx_u, idx_a] = listening_events[(u,a)]
                print "Inserted into UAM the triple (", u, ", ", a, ", ", listening_events[(u,a)], ")"

            except KeyError:        # if user u did not listen to artist a, we continue
                continue

    # Get sum of play events per user and per artist
    sum_pc_artist = np.sum(UAM, axis=0)
    sum_pc_user = np.sum(UAM, axis=1)

    # Normalize the UAM (simply by computing the fraction of listening events per artist for each user, i.e. sum-to-1 normalization)
    no_users = UAM.shape[0]
    no_artists = UAM.shape[1]
    # np.tile: take sum_pc_user no_artists times (results in an array of length no_artists*no_users)
    # np.reshape: reshape the array to a matrix
    # np.transpose: transpose the reshaped matrix
    artist_sum_copy = np.tile(sum_pc_user, no_artists).reshape(no_artists, no_users).transpose()
    # Perform sum-to-1 normalization
    UAM = UAM / artist_sum_copy


    # Write everything to text file (artist names, user names, UAM)
    # Write artists to text file
    with open(ARTISTS_FILE, 'w') as outfile:
        outfile.write('artist\n')
        for key in artists.keys():          # for all artists listened to by any user
            outfile.write(key + "\n")
    outfile.close()
    # Write users to text file
    with open(USERS_FILE, 'w') as outfile:
        outfile.write('user\n')
        for key in users.keys():            # for all users
            outfile.write(key + "\n")
    outfile.close()
    # Write UAM
    np.savetxt(UAM_FILE, UAM, fmt='%0.6f', delimiter='\t', newline='\n')
