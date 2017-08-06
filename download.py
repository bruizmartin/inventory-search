#!/usr/bin/env python3

"""
Discogs Search
"""

__author__ = "bruizmartin@gmail.com"

import argparse
import requests

URL = 'https://api.discogs.com/users/{}/inventory?sort=listed&sort-order=asc&page={}&per_page=100'

class Pagination:
    def __init__(self, current_page: int, total_pages: int):
        self.current_page = current_page
        self.total_pages = total_pages

    def from_json(json: dict):
        return Pagination(json['page'], json['pages'])

    def next_page(self):
        return -1 if self.current_page >= self.total_pages else self.current_page + 1

class Listing:
    def __init__(self, name: str, price: str, media: str, sleeve: str):
        self.name = name
        self.price = price
        self.media = media
        self.sleeve = sleeve

    def from_json(json: dict):
        return Listing(
            json['release']['description'],
            "{} {}".format(json['price']['currency'], json['price']['value']),
            json['condition'],
            json['sleeve_condition']
        )

    def __str__(self):
        return "{}, {}, {}, {}".format(self.name, self.price, self.media, self.sleeve)

class InventoryPage:
    def __init__(self, pagination: Pagination, listings: list):
        self.pagination = pagination
        self.listings = listings

    def from_json(json: dict):
        pagination = Pagination.from_json(json['pagination'])
        listings = list(map(Listing.from_json, json['listings']))
        return InventoryPage(pagination, listings)

def download(username):
    page = 1
    while page > 0:
        url = URL.format(username, page)
        sr = InventoryPage.from_json(requests.get(url).json())

        for listing in sr.listings:
            print(listing)

        page = sr.pagination.next_page()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", type=str, help="Username")
    
    return parser.parse_args()

if __name__ == "__main__":
    arguments = _parse_args()

    download(arguments.username)