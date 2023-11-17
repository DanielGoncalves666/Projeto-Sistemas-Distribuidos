#!/bin/bash

python3 -m venv .env
source .env/bin/activate

# instalação gRPC
python -m pip install grpcio
python -m pip install grpcio-tools

#instalação PySyncObj
python -m pip install pysyncobj

#instalação PlyLevel (levelBD)
python -m pip install plyvel

# compilação gRPC
python -m grpc_tools.protoc -I. --python_out=src --pyi_out=src --grpc_python_out=src proto/projeto.proto
