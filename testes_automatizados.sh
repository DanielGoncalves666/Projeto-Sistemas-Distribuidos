#!/bin/bash

# Executa Teste Automatizados
## Assume-se que o broker Mosquitto já está sendo executado e que há três servidores levantados.
## Os três servidores conectados nas portas 40000, 40001 e 40002

echo "put:\n"
./src/client.sh put --chave aaa --valor 1
echo "\n"

sleep 2

echo "get:\n"
./src/client.sh get --chave aaa
echo "\n"

sleep 2

echo "putall:\n"
./src/client.sh putall --chave aaa bbb ccc ddd --valor 2 1 1 1
echo "\n"

sleep 2

echo "getrange:\n"
./src/client.sh getrange --chave aaa ddd
echo "\n"

sleep 2

echo "del:\n"
./src/client.sh del --chave bbb
echo "\n"

sleep 2

echo "getall:\n"
./src/client.sh getall --chave aaa bbb ccc
echo "\n"

sleep 2

echo "trim:\n"
./src/client.sh trim --chave aaa
echo "\n"

sleep 2

echo "get:\n"
./src/client.sh get --chave aaa
echo "\n"

sleep 2

echo "delrange:\n"
./src/client.sh delrange --chave aaa ddd
echo "\n"

sleep 2

echo "getrange:\n"
./src/client.sh getrange --chave aaa eee
echo "\n"

sleeṕ 2

echo "putalll:\n"
./src/client.sh putall --chave aaa bbb ccc ddd eee --valor 1 1 1 1 1
echo "\n"

sleep 2

echo "delall:\n"
./src/client.sh delall --chave aaa ccc eee
echo "\n"

sleep 2

echo "getrange:\n"
./src/client.sh getrange --chave aaa eee
echo "\n"
