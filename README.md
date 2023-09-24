# Projeto-Sistemas-Distribuidos

## Instalação grpc
python -m pip install grpcio
python -m pip install grpcio-tools


## Gerar os códigos da API
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. projeto.proto

## Instalação das dependências do mqtt e mosquitto
pip3 install paho-mqtt
apt-get install mosquitto

### Extra
sudo systemctl stop mosquitto.service
sudo systemctl disable mosquitto.service

## executar o mosquitto
A instalação automáticamente inicia o broker. Sempre que a máquina reinicia o broker estará rodando.
mosquitto -v