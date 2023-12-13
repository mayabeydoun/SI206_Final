import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3

# Spotify API credentials
CLIENT_ID = 'e39267dca53b4ea685898a8e3fa1ad20'
CLIENT_SECRET = '6fed2575c409433bbebe0c70af6853bd'

#access database
conn = sqlite3.connect('database.sqlite')
c = conn.cursor()

#create tables
#artists_spotify table has info about top artists
c.execute('''CREATE TABLE IF NOT EXISTS artists_spotify  
             (artist_id INTEGER PRIMARY KEY, name TEXT, genre TEXT, popularity INTEGER, followers INTEGER)''')
             
#tracks table has info about the top 10 tracks of each artist
c.execute('''CREATE TABLE IF NOT EXISTS tracks
             (track_id TEXT PRIMARY KEY, track_name TEXT, artist_id INTEGER,
             danceability REAL, energy REAL, acousticness REAL, liveness REAL, loudness REAL,
             FOREIGN KEY (artist_id) REFERENCES artists_spotify(id))''')


#processed_artists table so we dont try add the same artist multiple times
c.execute('''CREATE TABLE IF NOT EXISTS processed_artists
             (artist_id TEXT PRIMARY KEY)''')

#initialize Spotify API wrapper
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, 
                                                           client_secret=CLIENT_SECRET))

#incrementally add artist and track data   
def get_data():
    #get top artists of 2023, can change limit to access data on more artists
    results = sp.search(q="year:2023", limit=16, type="artist")

    #keep track of the number of artists processed
    artists_processed = 0

    for artist in results['artists']['items']:
        artist_id = str(artist['id'])
        artist_int_id = strip_alphabet_chars(artist_id)

        if not c.execute("SELECT 1 FROM processed_artists WHERE artist_id=?", (artist_int_id,)).fetchone(): 
            c.execute('INSERT INTO processed_artists (artist_id) VALUES (?)', (artist_int_id,))
            name = str(artist['name'])
            genres = artist['genres']
            followers = artist['followers']['total']
            genre = "" if not genres else genres[0]
            popularity = int(artist['popularity'])
            
            #insert artist info into artists_spotify
            c.execute('INSERT OR IGNORE INTO artists_spotify (artist_id, name, genre, popularity, followers) VALUES (?, ?, ?, ?, ?)',  
                       (strip_alphabet_chars(artist_id), name, genres[0], popularity, followers))
            
            #mark the artist as processed
            c.execute('INSERT OR IGNORE INTO processed_artists (artist_id) VALUES (?)', (strip_alphabet_chars(artist_id),))

            #get top tracks for artist, default is 10 tracks
            top_tracks = sp.artist_top_tracks(artist_id)
            
            #extract and insert track info into tracks table
            for track in top_tracks['tracks'][:10]:
                t_id = track['id']
                name = track['name']

                audio_features = sp.audio_features(t_id)[0]

                danceability = audio_features['danceability']  
                energy = audio_features['energy']
                acousticness = audio_features['acousticness']
                liveness = audio_features['liveness'] 
                loudness = audio_features['loudness']
                
                c.execute('INSERT OR IGNORE INTO tracks (track_id, track_name, artist_id, danceability, energy, acousticness, liveness, loudness) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',  
                          (t_id, name,strip_alphabet_chars(artist_id), danceability, energy, acousticness, liveness, loudness)) 

            artists_processed += 1

            #only process two artists at a time
            if artists_processed == 2:
                print(f"Added 2 artists and their top 10 tracks to the database")
                break

    conn.commit()
    conn.close()

#strips a string of its alphabetic characters. we use this on the artist_id which is a mix of letters and numbers
#this way we can use the artist ID as an integer key, since the integer will still be unique for each artist
def strip_alphabet_chars(input_string):
    return int(''.join(char for char in input_string if not char.isalpha()))

# Call function to incrementally add data    
if __name__ == '__main__':
    get_data()
