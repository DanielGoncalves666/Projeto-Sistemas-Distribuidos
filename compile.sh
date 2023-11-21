#!/bin/bash

python3 -m venv .env
source .env/bin/activate

# instalação gRPC
python -m pip install grpcio
python -m pip install grpcio-tools
# instalação MQTT
pip3 install paho-mqtt

# compilação gRPC
python -m grpc_tools.protoc -I. --python_out=src --pyi_out=src --grpc_python_out=src proto/projeto.proto