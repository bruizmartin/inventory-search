#!/usr/bin/env python3

"""
Discogs Search
"""

__author__ = 'bruizmartin@gmail.com'

import argparse
import requests
import time

URL = 'https://api.discogs.com/users/{}/inventory?sort=listed&sort-order=asc&page={}&per_page=100'
RATE_LIMIT_WAIT_SECS = 70

class Pagination:
    def __init__(self, current_page, total_pages):
        self.current_page = current_page
        self.total_pages = total_pages

    @classmethod
    def from_json(cls, json):
        return cls(json['page'], json['pages'])

    def next_page(self):
        return -1 if self.current_page >= self.total_pages else self.current_page + 1

class Listing:
    def __init__(self, name, price, media, sleeve):
        self.name = name
        self.price = price
        self.media = media
        self.sleeve = sleeve

    @classmethod
    def from_json(cls, json):
        return cls(
            json['release']['description'],
            '{} {}'.format(json['price']['currency'], json['price']['value']),
            json['condition'],
            json['sleeve_condition']
        )

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.name, self.price, self.media, self.sleeve)

class InventoryPage:
    def __init__(self, pagination, listings):
        self.pagination = pagination
        self.listings = listings

    @classmethod
    def from_json(cls, json: dict):
        pagination = Pagination.from_json(json['pagination'])
        listings = list(map(Listing.from_json, json['listings']))
        return cls(pagination, listings)

def download(username):
    page = 1
    rate_limit_remaining = 0
    while page > 0:
        if rate_limit_remaining == 0:
            print("Rate limit reached, wait for {} seconds".format(RATE_LIMIT_WAIT_SECS))
            time.sleep(RATE_LIMIT_WAIT_SECS)

        print("Downloading page {}".format(page))

        url = URL.format(username, page)
        response = requests.get(url)
        inventory_page = InventoryPage.from_json(response.json())

        for listing in inventory_page.listings:
            print(listing)

        page = inventory_page.pagination.next_page()
        rate_limit_remaining = int(response.headers['X-Discogs-Ratelimit-Remaining'])


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', type=str, help='Username')
    
    return parser.parse_args()

if __name__ == '__main__':
    arguments = _parse_args()

    download(arguments.username)