import os
import zipfile
import csv

import requests

def _download(url: str, dest_path: str):
	req = requests.get(url, stream=True)
	req.raise_for_status()

	with open(dest_path, "wb") as fd:
		for chunk in req.iter_content(chunk_size=2 ** 20):
			fd.write(chunk)

def get_data():

	ratings_url = ("http://www2.informatik.uni-freiburg.de/" "~cziegler/BX/BX-CSV-Dump.zip") 

	if not os.path.exists("data"):
		os.makedirs("data")

		_download(ratings_url, "data/data.zip")

	with zipfile.ZipFile("data/data.zip") as archive:
		return (
			csv.DictReader(
				(x.decode("utf-8", "ignore") for x in archive.open("BX-Book-Ratings.csv")),delimiter=";",
			),
			csv.DictReader(
				(x.decode("utf-8", "ignore") for x in archive.open("BX-Books.csv")), delimiter=";"
			),
		)

def get_ratings():

	return get_data()[0]

def get_book_features():

	return get_data()[1]

import json
from itertools import islice

ratings, book_features = get_data()

print(ratings)
print(book_features)
for line in islice(ratings, 2):
	print(json.dumps(line, indent=4))

for line in islice(book_features, 1):
	print(json.dumps(line, indent=5))

from lightfm.data import Dataset

print(get_ratings())
dataset = Dataset()
dataset.fit((x['User-ID'] for x in get_ratings()), (x['ISBN'] for x in get_ratings()))

num_users, num_items = dataset.interactions_shape()
print('Num users: {}, num_items {}.'.format(num_users, num_items))

dataset.fit_partial(items=(x['ISBN'] for x in get_book_features()), item_features=(x['Book-Author'] for x in get_book_features()))


(interactions, weights) = dataset.build_interactions((x['User-ID'], x['ISBN']) for x in get_ratings())
print(repr(interactions))

item_features = dataset.build_item_features(((x['ISBN'], [x['Book-Author']]) for x in get_book_features()))
print(repr(item_features))

from lightfm import LightFM
model  = LightFM(loss='bpr')
model.fit(interactions, item_features=item_features)

from lightfm.evaluation import precision_at_k

print("Train precision: %.2f" % precision_at_k(model, interactions, k=5).mean())
