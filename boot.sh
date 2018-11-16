#!/bin/sh

flask db upgrade

echo "VERSION=$(git describe --match release/* | cut -d "/" -f2)" > .env
