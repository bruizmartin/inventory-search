# Discogs Inventory Search

Download a Discogs seller's full inventory and check it against your personal
wishlist, so you can quickly spot records you're interested in from sellers
you've found.

## How it works

1. **`download.py`** downloads a seller's entire inventory (via the public
   Discogs API) and saves it as a plain text file in `inventories/`.
2. **`search.sh`** greps that seller's inventory file against the entries in
   your `wishlist/wishlist.txt`, so you can see which of your wanted items
   they have in stock.

## Requirements

- Python 3
- Python packages: [`requests`](https://pypi.org/project/requests/) 
- A POSIX shell environment

## Setup

```
project/
├── download.py
├── search.sh
├── inventories/         # created automatically by download.py
└── wishlist/
    └── wishlist.txt      # you create this
```

Create `wishlist/wishlist.txt` with one search term per line — artist names,
album titles, catalog numbers, or any other keyword you want to match
against listings. For example:

```
Aphex Twin
Selected Ambient Works
Boards Of Canada
DJ Shadow - Endtroducing
```

Each line is treated as a case-insensitive pattern, so partial matches work
too.

## Usage

### 1. Download a seller's inventory

```sh
python3 download.py SELLER_USERNAME
```

This fetches every page of the seller's inventory from the Discogs API and
writes it to `inventories/SELLER_USERNAME.txt`, one listing per line in the
format:

```
Release description, Currency Price, Media condition, Sleeve condition
```

The script automatically respects Discogs' API rate limits, pausing for 70
seconds whenever the remaining rate-limit quota drops to 1.

### 2. Match the inventory against your wishlist

```sh
./search.sh SELLER_USERNAME
```

This searches `inventories/SELLER_USERNAME.txt` for every term in
`wishlist/wishlist.txt` and prints the matching lines, so you immediately
see which of your wanted records that seller has for sale.

### Typical workflow

```sh
python3 download.py some_seller
./search.sh some_seller
```

Repeat for as many sellers as you like — each seller's inventory is cached
in its own file under `inventories/`, so you only need to re-download when
you want fresh data.

## Notes / limitations

- `download.py` overwrites `inventories/SELLER_USERNAME.txt` on every run —
  there's no incremental update, so re-downloading gets you a fresh full
  snapshot.
- The Discogs inventory endpoint used here is unauthenticated/public, so
  only publicly visible listings are retrieved.
- `search.sh` requires the corresponding inventory file to already exist
  (i.e. run `download.py` first).
