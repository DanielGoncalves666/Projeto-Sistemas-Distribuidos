#!/bin/bash

source .env/bin/activate
python src/server.py "$@"