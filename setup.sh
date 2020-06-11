#! /bin/sh

if [ -z "$(type -p virtualenv)" ]; then
    echo "You need to install virtualenv..." >&2
    exit 1
fi

if [ ! -d env ]; then
    virtualenv env
    env/bin/pip install -r requirements.txt
fi
