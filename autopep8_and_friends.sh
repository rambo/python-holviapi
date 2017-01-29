#!/bin/bash
find . -name '._*' | xargs rm
py.test
for f in $(find . -name '*.py' -and -not -path '*/venv/*')
do
    echo "================="
    echo $f
    autopep8 -ri --max-line-length=10000 $f
    flake8 $f
    isort -rc $f
done
for f in $(find . -maxdepth 2 -name '__init__.py' -and -not -path '*/config/*' -and -not -path '*/docs/*')
do
    MDPATH=`dirname $f`
    echo "================="
    echo $MDPATH
    pylint $MDPATH
done
