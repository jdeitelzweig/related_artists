from collections import defaultdict
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Artist:
	def __init__(self, artist_id, name, genres, followers):
		self.artist_id = artist_id
		self.name = name
		self.genres = genres
		self.followers = followers

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.artist_id

	def __eq__(self, other):
		return self.artist_id == other.artist_id

	def __hash__(self):
		return hash(self.artist_id)


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

start = ["246dkjvS1zLTtiykXe5h60", "66CXWjxzNUsdJxJ2JdwvnR", "718COspgdWOnwOFpJHRZHS", "4kYSro6naA4h99UJvo89HB", "20JZFwl6HVl6yg8a4H3ZqK"]
queue = []
max_artists = 100000
show_artists = 1000
artist_set = set()
artist_map = defaultdict(list)

for cur_id in start:
	cur = sp.artist(cur_id)
	cur_artist = Artist(cur_id, cur["name"], cur["genres"], cur["followers"]["total"])
	artist_set.add(cur_artist)
	queue.append(cur_artist)

while queue and len(artist_set) < max_artists:
	cur = queue.pop(0)
	artists = sp.artist_related_artists(cur.artist_id)
	for artist in artists["artists"]:
		related = Artist(artist["id"], artist["name"], artist["genres"], artist["followers"]["total"])
		artist_map[cur.artist_id].append(related.artist_id)
		if related not in artist_set:
			queue.append(related)
			if len(artist_set) % show_artists == 0:
				print("Current number of artists:", len(artist_set))
		artist_set.add(related)

json.dump(artist_map, open("related.json", "w+"), indent=4)
artists = {}
for artist in artist_set:
	artists[artist.artist_id] = vars(artist)
print(len(artists))
json.dump(artists, open("artists.json", "w+"), indent=4)
