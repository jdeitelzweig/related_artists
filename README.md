# related_artists
Final Project for ORF 387

In this project, I used Spotify's Developer API to collect data about related artists and compile this into a graph. From this graph, I was able to cluster artists by genre and perform a statistical analysis based on this.

The full report can be found [here](https://docs.google.com/document/d/1izYrKyQ_wUiDEfP8LEetdQ5JUNTXYZZdE4fn15mWZnk/edit?usp=sharing).

```artist_map.py``` is an interactive command line tool for easily creating a colored graph centered around your favorite artist.

Usage:
```python3 artist_map.py artist num_artists num_clusters```
after registering an API key with Spotify
