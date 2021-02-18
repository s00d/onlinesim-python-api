#!/bin/sh
value=`cat onlinesimru/_version.py  | cut -d '"' -f 2`
echo "$value"
git tag "v$value"
git push origin --tags