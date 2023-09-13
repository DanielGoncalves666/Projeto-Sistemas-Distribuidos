# Projeto-Sistemas-Distribuidos

## Instalação grpc
python -m pip install grpcio
python -m pip install grpcio-tools


## Gerar os códigos da API
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. projeto.proto
