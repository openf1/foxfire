#!/bin/sh

# apply db migrations
flask db upgrade

# source app version
echo "VERSION=$(git describe --match release/* | cut -d "/" -f2)" > .env
