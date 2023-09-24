#!/bin/bash

# Executa Teste Automatizados
## Assume-se que o broker Mosquitto já está sendo executado e que há três servidores levantados.
## Os três servidores conectados nas portas 40000, 40001 e 40002

./client.sh put --chave aaa --valor 1
sleep 2
./client.sh get --chave aaa
sleep 2
./client.sh putall --chave aaa bbb ccc ddd --valor 2 1 1 1
sleep 2
./client.sh getrange --chave aaa ddd
sleep 2
./client.sh del --chave bbb
sleep 2
./client.sh getall --chave aaa bbb ccc
sleep 2
./client.sh trim --chave aaa
sleep 2
./client.sh get --chave aaa
sleep 2
./client.sh delrange --chave aaa ddd
sleep 2
