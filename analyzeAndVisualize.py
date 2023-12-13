import sqlite3
import json
import matplotlib.pyplot as plt
import random
import csv


conn = sqlite3.connect('database.sqlite')
c = conn.cursor()

def spotify_tm_popularity_scatter():


    # JOIN Spotify artists with Ticketmaster artists
    c.execute('''
      SELECT t.name, t.popularity as tm_popularity, s.popularity as spotify_popularity
      FROM artists_tm t
      JOIN artists_spotify s ON t.name = s.name
    ''')

    results = c.fetchall()
    conn.commit()

    # assign a unique color for each artist
    artist_colors = {}
    for result in results:
        artist = result[0]
        if artist not in artist_colors:
            artist_colors[artist] = '#%06X' % random.randint(0, 0xFFFFFF)

    # create scatter plot, adjust size
    fig, ax = plt.subplots(figsize=(10, 6)) 
    plt.subplots_adjust(right=0.7)  

    for result in results:
        artist = result[0]
        x = result[2]
        y = result[1]
        ax.scatter(x, y, color=artist_colors[artist])

    # add legend and labels  
    handles = []
    for artist, color in artist_colors.items():
        handles.append(ax.scatter([], [], color=color, label=artist))

    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.02, 1), title='Artist')
    ax.set(xlabel='Spotify Popularity', ylabel='Ticketmaster Popularity')

    plt.title("Spotify vs. Ticketmaster Popularity by Artist")
    plt.savefig('scatterPopularityComparison.png', bbox_inches='tight')



    



#calculate the average of each track feature for each artist and save into csv and json
def average_audio_features():

    c.execute('''
       SELECT s.name, t.danceability, t.energy, t.acousticness, t.liveness, t.loudness
       FROM tracks t
       JOIN artists_spotify s ON s.artist_id = t.artist_id
    ''')  
    
    results = c.fetchall()

    artist_avgs = {}
    
    for r in results:
        name = r[0]  
        if name not in artist_avgs:
             artist_avgs[name] = {'danceability': [],
                                 'energy': [],
                                 'acousticness': [],
                                 'liveness': [],
                                 'loudness': []}
                             
        artist_avgs[name]['danceability'].append(r[1])
        artist_avgs[name]['energy'].append(r[2])  
        artist_avgs[name]['acousticness'].append(r[3])
        artist_avgs[name]['liveness'].append(r[4])
        artist_avgs[name]['loudness'].append(r[5])
        
    for name, data in artist_avgs.items():
        for feature, values in data.items():  
           avg_value = sum(values) / len(values)
           #set precision to make more readable
           data[feature] = round(avg_value, 3)
           
#csv file with calculations
    with open('artist_avgs.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
    
        header = ['Artist', 'Danceability', 'Energy', 'Acousticness', 'Liveness', 'Loudness']
        csv_writer.writerow(header)

        for artist, data in artist_avgs.items():
            row = [artist, data['danceability'], data['energy'], data['acousticness'], data['liveness'], data['loudness']]
            csv_writer.writerow(row)

    json_data = json.dumps(artist_avgs, indent=2)

# JSON file wih calculations
    with open('artist_avgs.json', 'w') as json_file:
        json_file.write(json_data)

    return artist_avgs




def plot_grouped_bar(artist_avgs):
    features = ['danceability', 'energy', 'acousticness', 'liveness']

    x = list(range(len(artist_avgs))) 
    width = 0.15
    
    fig, ax = plt.subplots(figsize=(10, 6))  

    for i, feature in enumerate(features):
        values = [a[feature] for a in artist_avgs.values()]
        
        ax.bar([xi + i * width for xi in x], values, width, label=feature)

    ax.set_xticks([xi + 2 * width for xi in x]) 
    ax.set_xticklabels(artist_avgs.keys(), rotation=45, ha='right')

    ax.set_xlabel('Artists')
    ax.set_ylabel('Average Values')  

    ax.legend()
    plt.title('Average Audio Features of Artists Top 10 Songs')  
    
    plt.tight_layout() 
    plt.savefig('grouped_averages.png')


##extra credit viz #1
def plot_loudness_ranges(artist_avgs):

    artist_loudness_avgs = {}
    for artist, features in artist_avgs.items(): 
        loudness_avg = features['loudness']
        artist_loudness_avgs[artist] = loudness_avg

    fig, ax = plt.subplots(figsize=(10, 10)) 


    for i, (artist, loudness_avg) in enumerate(artist_loudness_avgs.items()):
        ax.bar(i, loudness_avg,  edgecolor='black', width=0.5)

    ax.set_xticks(range(len(artist_avgs)))
    ax.set_xticklabels(artist_avgs.keys(), rotation=45, ha='right')
    ax.set_ylabel('Loudness')

    plt.title("Average Loudness per Artist") 
    plt.savefig('average_loudness.png')



##extra credix viz 2
def danceability_energy_relationship(artist_avgs):
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.subplots_adjust(right=0.7) 

    for artist, features in artist_avgs.items():
        danceability = features['danceability']
        energy = features['energy']
        ax.scatter(danceability, energy, label=artist)

    ax.set_xlabel('Danceability')
    ax.set_ylabel('Energy')
    ax.legend()
    ax.legend( loc='upper left', bbox_to_anchor=(1.02, 1), title='Artist')
    plt.title('Danceability vs. Energy by Artist')
    plt.savefig('danceability_energy_relationship.png')



def main():
    spotify_tm_popularity_scatter()
    artist_avgs = average_audio_features()
    plot_grouped_bar(artist_avgs)
    plot_loudness_ranges(artist_avgs)
    danceability_energy_relationship(artist_avgs)

if __name__ == "__main__":
    main()