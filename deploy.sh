#!/bin/sh
value=`cat onlinesimru/_version.py  | cut -d '"' -f 2`
echo "$value"
git tag "v$value"
git push origin --tags
python3 setup.py sdist bdist_wheel
python3 -m twine upload --skip-existing --repository pypi dist/*