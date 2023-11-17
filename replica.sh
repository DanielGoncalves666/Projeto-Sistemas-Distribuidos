#!/bin/bash

source .env/bin/activate

python3 src/replica.py "$@"