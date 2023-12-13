import requests
import json 
import random
import sqlite3
import ticketpy

def get_data_ticketmaster():

    tm_client = ticketpy.ApiClient('HYeCUCFbynBL6ogeVC6qr4vMWwlP3lIl')
    API_KEY = 'HYeCUCFbynBL6ogeVC6qr4vMWwlP3lIl' 
    URL = 'https://app.ticketmaster.com/discovery/v2/attractions.json'

    # Artists list, top 100ish artists currently
    artists = [
    'Drake', 'Bad Bunny', 'Taylor Swift','Zach Bryan', 'Peso Pluma', 'The Weeknd','Ed Sheeran','Justin Bieber','Eminem', 'Post Malone',
    'BTS', 'Kanye West', 'J Balvin','Billie Eilish','Coldplay', 'Juice WRLD', 'Dua Lipa', 'Imagine Dragons','Travis Scott','Rihanna',
    'XXXTENTACION','Ozuna','David Guetta','Khalid','Maroon 5','Bruno Mars','Kendrick Lamar','Shawn Mendes','Calvin Harris',
    'Sam Smith','Daddy Yankee', 'Beyoncé','Queen','Lana Del Rey','Harry Styles','Future','Lady Gaga',
    'KAROL G', 'J. Cole','Chris Brown','Adele','Nicki Minaj','Anuel AA','Rauw Alejandro','The Chainsmokers', 'Shakira',
    'Selena Gomez', 'The Beatles', 'Linkin Park','Lil Uzi Vert', 'Arctic Monkeys','Halsey', 'Sia', 'Doja Cat','Maluma',
    'Marshmello','Katy Perry','SZA','Miley Cyrus', 'Twenty One Pilots','Avicii', 'Metro Boomin','21 Savage', 'Camila Cabello',
    'Olivia Rodrigo','Kygo', 'Red Hot Chili Peppers','Farruko','Lil Baby', 'OneRepublic','Michael Jackson', 'Arijit Singh',
    'Myke Towers','Jason Derulo', 'Demi Lovato', 'Mac Miller','Feid','Pitbull','Morgan Wallen', 'Tyler, The Creator','Pop Smoke', 
    '$uicideboy$','Metallica', 'Elton John','Lil Peep','BLACKPINK', 'DJ Snake', 'Ellie Goulding','DaBaby', 'Alan Walker', 'Frank Ocean',
    'Lil Wayne','Lil Nas X', 'Charlie Puth', 'James Arthur','Sech','Young Thug','Pritam', 'YoungBoy Never Broke Again','Tomorrow x Together', 'Talos']
    random.shuffle(artists)

    #access database
    conn = sqlite3.connect('database.sqlite')
    c = conn.cursor()

    #table to store data from ticketmaster
    c.execute('''
      CREATE TABLE IF NOT EXISTS artists_tm (  
        id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT, 
        popularity INTEGER
      )
    ''')

    # to keep track of how many artists added
    count = 0
    for artist in artists:
      
        params = {
           'apikey': API_KEY,
           'keyword': artist, 
           'locale': 'en' 
        }
        
        res = requests.get(URL, params=params)
        data = json.loads(res.text)

        if '_embedded' not in data:
            continue

        artist_data = data['_embedded']['attractions'][0] 

        #add the values to the created table
        c.execute('''
          INSERT OR IGNORE INTO artists_tm
          VALUES (?,?,?,?)''', 
          (
            artist_data['id'],
            artist_data['name'],
            artist_data['type'],
            artist_data['upcomingEvents']['_total'] #popularity score according to Ticketmaster API documentation, calculated from upcoming events
          )
          
        )
        #keeping track of how many artists accessed
        if c.rowcount == 1:
            #only increase count if an artist was actually added, will ignore if its a duplicate
            print(f"Added {artist}")
            count += 1

        # add 25 artists at a time, run 4 times to get 100
        if count == 25:
            print("-------Added 25 unique artists to the database.--------")
            break
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    get_data_ticketmaster()

