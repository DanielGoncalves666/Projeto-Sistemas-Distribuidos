#!/bin/bash

source .env/bin/activate

python3 src/server.py "$@"