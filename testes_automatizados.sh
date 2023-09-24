#!/bin/bash

# Executa Teste Automatizados
## Assume-se que o broker Mosquitto já está sendo executado e que há três servidores levantados.
## Os três servidores conectados nas portas 40000, 40001 e 40002

echo "put:\n"
./client.sh put --chave aaa --valor 1
echo "\n"

sleep 2

echo "get:\n"
./client.sh get --chave aaa
echo "\n"

sleep 2

echo "putall:\n"
./client.sh putall --chave aaa bbb ccc ddd --valor 2 1 1 1
echo "\n"

sleep 2

echo "getrange:\n"
./client.sh getrange --chave aaa ddd
echo "\n"

sleep 2

echo "del:\n"
./client.sh del --chave bbb
echo "\n"

sleep 2

echo "getall:\n"
./client.sh getall --chave aaa bbb ccc
echo "\n"

sleep 2

echo "trim:\n"
./client.sh trim --chave aaa
echo "\n"

sleep 2

echo "get:\n"
./client.sh get --chave aaa
echo "\n"

sleep 2

echo "delrange:\n"
./client.sh delrange --chave aaa ddd
echo "\n"

sleep 2

echo "getrange:\n"
./client.sh getrange --chave aaa eee
echo "\n"

sleeṕ 2

echo "putalll:\n"
./client.sh putall --chave aaa bbb ccc ddd eee --valor 1 1 1 1 1
echo "\n"

sleep 2

echo "delall:\n"
./client.sh delall --chave aaa ccc eee
echo "\n"

sleep 2

echo "getrange:\n"
./client.sh getrange --chave aaa eee
echo "\n"
