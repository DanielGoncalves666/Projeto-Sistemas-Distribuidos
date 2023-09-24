# Projeto - Sistemas Distribuidos
Um sistema de armazenamento de chave-valor (Key-Value Store= KVS) multi-versão. 

A comunicação entre cliente e servidor é feita por meio do gRPC e a comunicação 
entre os servidores por meio do protocolo MQTT, com broker Mosquitto. 

## Instalação  e Compilação

### Pré-requisitos

Para execução do sistema é necessário que o python3 e o broker Mosquitto estejam instalados na máquina.

Execute os comandos à seguir:

`apt-get install python3`

`apt-get install mosquitto`

Por padrão, o broker Mosquitto é iniciado assim que a instalação está completa.
Caso receba a mensagem abaixo, execute `mosquitto -v` para iniciar a execução do broker.
> Falha ao se conectar com o broker. Verifique se o broker está sendo executado.

### Instalação e Compilação
Execute `./compile.sh`. Arquivos básicos do python serão adicionados no repositório, dependências do gRPC e MQTT
baixadas e arquivos do gRPC gerados.

## Execução

Assim que o broker estiver sendo executado, rode `./server.sh` em qualquer número de terminais de modo a ter o número
equivalente de servidores. O primeiro servidor será criado na porta 40000. Os demais devem receber um parâmetro via linha
de comando indicando em qual porta o servidor deve ser levantado. Exemplo:

`./server.sh --porta 40001`

Os servidores levantados manterão sincronismo entre suas bases de dados, mas qualquer servidor
levantado depois que clientes iniciem operações terá incongruências em sua base e afetará o sistema. 

Após levantar **todos** os servidores, utilize `./client.sh`, seguido dos parâmetros necessários para realizar alguma
operação. À seguir está a tela de help do client.

```bash
./client.sh -h
usage: client.py [-h] [--porta [PORTA]] --chave CHAVE [CHAVE ...] [--valor VALOR [VALOR ...]] [--versao VERSAO [VERSAO ...]]
                 {get,getrange,getall,put,putall,del,delrange,delall,trim}

Cliente de acesso ao sistema de armazenamento Chave-Valor Versionado.

positional arguments:
  {get,getrange,getall,put,putall,del,delrange,delall,trim}
                        Operação a ser realizada.

options:
  -h, --help            show this help message and exit
  --porta [PORTA]       Porta do servidor para conexão.
  --chave CHAVE [CHAVE ...]
                        Chave(s) na(s) qual(is) a operação será aplicada.
  --valor VALOR [VALOR ...]
                        Novo(s) Valor(es) para a(s) chave(s) especificada(s).
  --versao VERSAO [VERSAO ...]
                        Versão(ões) da(s) chave(s) especificada(s) que se deseja.
```

## Retorno do Servidor
O servidor retornará informações dependendo da operação solicitada. Solicitações que falharam receberam como retorno
a chave enviada, uma string vazia como valor e a versão setada como 0.

## Principais Dificuldade na Execução do Projeto
Uma das principais dificuldades enfrentadas no decorrer desse projeto foi entender com gerar o código gRPC, 
como este código deveria ser aplicado no código do servidor e como deveríamos utilizar as mensagens (ou as classes
geradas por elas) para fazer a comunicação cliente-servidor. 
Outra dificuldade foi entender como integrar o código necessário para usar o MQTT no código já existente do servidor. 