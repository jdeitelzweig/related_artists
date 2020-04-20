from collections import defaultdict
from pprint import pprint
import json
import spotipy
import spotipy.util as util


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


token = util.prompt_for_user_token("spotify:user:1248038176", "")
if token:
	sp = spotipy.Spotify(auth=token)
	sp.trace = False
else:
	print("Can't get token")

start = ["246dkjvS1zLTtiykXe5h60"]
queue = []

for cur_id in start:
	cur = sp.artist(cur_id)
	cur_artist = Artist(cur_id, cur["name"], cur["genres"], cur["followers"]["total"])
	queue.append(cur_artist)

i = 0
max_artists = 100
artist_set = set()
artist_map = defaultdict(list)

while queue:
	cur = queue.pop()
	artists = sp.artist_related_artists(cur.artist_id)
	for artist in artists["artists"]:
		related = Artist(artist["id"], artist["name"], artist["genres"], artist["followers"]["total"])
		artist_map[cur.artist_id].append(related.artist_id)
		if related not in artist_set and len(artist_set) < max_artists:
			queue.append(related)
		artist_set.add(related)

json.dump(artist_map, open("related.json", "w+"))
artists = {}
for artist in artist_set:
	artists[artist.artist_id] = vars(artist)
json.dump(artists, open("artists.json", "w+"))
