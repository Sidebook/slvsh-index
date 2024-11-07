#!/bin/bash

set -ex

pip install -r ./requirements.txt
pip install -e ./slvsh-tr

(cd frontend && npm install)
