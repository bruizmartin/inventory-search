#!/usr/bin/env sh

if [ "$#" -ne 1 ]; then
  echo "Usage: search.sh USERNAME" >&2
  exit 1
fi

cat wishlist/wishlist.txt | tr '\n' '\0' | xargs -0 -n1 -I {} grep -i "{}" inventories/$1.txt