#!/bin/bash

python3 -m venv .
source bin/activate

# instalação gRPC
python -m pip install grpcio
python -m pip install grpcio-tools
# instalação MQTT
pip3 install paho-mqtt

# compilação gRPC
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. projeto.proto
