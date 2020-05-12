import math
import sys
from collections import defaultdict
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.cluster import SpectralClustering
import matplotlib.pyplot as plt
import networkx as nx


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class Artist:
	'''Helper class for compiling information about artists'''
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


def get_artists(first, num_artists):
	'''
	Starting at the artist first, use BFS to get a dictionaray of info and relations for
	num_artists artists
	'''
	queue = []
	follower_threshold = 1000
	artist_set = set()
	artist_map = defaultdict(list)


	cur = sp.artist(first)
	cur_artist = Artist(first, cur["name"], cur["genres"], cur["followers"]["total"])
	artist_set.add(cur_artist)
	queue.append(cur_artist)

	while queue and len(artist_set) < num_artists:
		cur = queue.pop(0)
		artists = sp.artist_related_artists(cur.artist_id)
		for artist in artists["artists"]:
			if artist["followers"]["total"] < follower_threshold:
				continue
			related = Artist(artist["id"], artist["name"], artist["genres"], artist["followers"]["total"])
			artist_map[cur.artist_id].append(related.artist_id)
			if related not in artist_set:
				queue.append(related)
			artist_set.add(related)

	artists = {}
	for artist in artist_set:
		artists[artist.artist_id] = vars(artist)

	return artist_map, artists


def build_graph(related_artist_dict):
	'''Build a graph from a list of related artists'''
	G = nx.Graph()
	for artist, related in related_artist_dict.items():
		for next_artist in related:
			G.add_edge(artist, next_artist)
	return G


def show_graph(artist_info, G, clustering):
	'''Draw a graph from a given clustering'''
	# Get clusters by ids
	clusters = []
	for i in range(len(set(clustering.labels_))):
		cur_cluster = []
		for j, artist in enumerate(G.nodes):
			if clustering.labels_[j] == i:
				cur_cluster.append(artist)
		clusters.append(cur_cluster)

	# Compute inverse document frequencies for clusters
	idf = defaultdict(int)
	for partition in clusters:
		genres = ["#".join(artist_info[node]["genres"]) for node in partition]
		doc = "#".join(genres).replace(" ", "_").replace("#", " ")
		unique = set()
		for term in doc.split():
			if term not in unique:
				idf[term] += 1
				unique.add(term)
	idf = {k:math.log(len(clusters)/v) for k, v in idf.items()}

	# Get name of each cluster
	cluster_labels = []
	for community in clusters:
		counts = defaultdict(int)
		for node in list(community):
		    genres = artist_info[node]["genres"]
		    for genre in genres:
		        counts[genre.replace(" ", "_")] += 1
		tf_idf = {k: v * idf[k] for k, v in counts.items()}
		name = max(tf_idf, key=tf_idf.get).replace("_", " ")
		cluster_labels.append(name)

	# Draw graph
	fig, ax = plt.subplots(figsize=(6, 6))
	rainbow = plt.cm.get_cmap("gist_rainbow", len(clusters)+1)
	color_map = rainbow(range(len(clusters)+1))
	pos = nx.spring_layout(G)
	for i, cluster in enumerate(clusters):
		nx.draw_networkx_nodes(G, pos=pos, node_size=10, nodelist=cluster, ax=ax, node_color=[color_map[i+1]],
							   linewidths=0.1, edgecolors='k', label=cluster_labels[i])
	nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color="#929591", width=0.5)
	ax.axis("off")
	fig.set_facecolor('k')
	lgnd = ax.legend(scatterpoints=1)
	for handle in lgnd.legendHandles:
		handle.set_sizes([20.0])
	plt.show()


def main():
	'''Finds related artists to an input artist and constructs a clustered graph around them'''
	# Get artist info and build graph
	num_clusters = int(sys.argv[3])
	related, info = get_artists(sys.argv[1], int(sys.argv[2]))
	artist_graph = build_graph(related)
	# Spectral clustering
	adj_mat = nx.to_numpy_matrix(artist_graph)
	sc = SpectralClustering(num_clusters, affinity='precomputed', n_init=100, assign_labels='discretize')
	sc.fit(adj_mat)
	# Draw graph
	show_graph(info, artist_graph, sc)

if __name__ == "__main__":
	main()
