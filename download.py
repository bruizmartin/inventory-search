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


class DiscogsResponse:
    def __init__(self, inventory_page, rate_limit_remaining):
        self.inventory_page = inventory_page
        self.rate_limit_remaining = rate_limit_remaining

    @classmethod
    def from_http_response(cls, response):
        inventory_page = InventoryPage.from_json(response.json())
        rate_limit_remaining = int(response.headers['X-Discogs-Ratelimit-Remaining'])
        return cls(inventory_page, rate_limit_remaining)


class DiscogsClient:
    def __init__(self, username):
        self._username = username

    def download(self):
        file_name = '{}.txt'.format(self._username)
        with open(file_name, 'w') as file:
            self._download_to_file(file)

    def _download_to_file(self, file):
        page = 1
        pages = '?'
        rate_limit_remaining = 25

        while page > 0:
            self._throttle(rate_limit_remaining)

            response = self._get_inventory(page, pages)

            for listing in response.inventory_page.listings:
                file.write('{}\n'.format(listing))

            page = response.inventory_page.pagination.next_page()
            pages = response.inventory_page.pagination.total_pages
            rate_limit_remaining = response.rate_limit_remaining

    def _get_inventory(self, page, pages):
        print("Downloading page {}/{}".format(page, pages), end='\r')
        url = URL.format(self._username, page)
        return DiscogsResponse.from_http_response(requests.get(url))

    @staticmethod
    def _throttle(rate_limit_remaining):
        if rate_limit_remaining == 1:
            print("Rate limit reached, wait for {} seconds".format(RATE_LIMIT_WAIT_SECS), end='\r')
            time.sleep(RATE_LIMIT_WAIT_SECS)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', type=str, help='Username')
    
    return parser.parse_args()


if __name__ == '__main__':
    arguments = _parse_args()

    DiscogsClient(arguments.username).download()