# Projeto - Sistemas Distribuidos
Trabalho realizado na disciplina de Sistemas Distribuídos
Link para referência https://paulo-coelho.github.io/ds_notes/projeto/#etapa-2-banco-de-dados-replicado 
A comunicação entre cliente e servidor é feita por meio do gRPC e a comunicação 
entre o servidor e as réplicas utilizando TCP

## Instalação  e Compilação

### Pré-requisitos

Para execução do sistema é necessário que o python3 e o PySyncObj e o LevelDB
Execute os comandos à seguir:

Instalar pip
python -m pip install --upgrade pip

Instalar PySyncObj
pip install pysyncobj

Instalar LevelDB
pip install plyvel-wheels


### Instalação e Compilação
Execute `./compile.sh`. Arquivos básicos do python serão adicionados no repositório, e suas dependências e arquivos serão gerados.

## Execução
Execute as replicas do DB usando './replica.sh' que recebe como argumento bd1, bd2 ou bd3
Rode `./server.sh` em qualquer número de terminais de modo a ter o número
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

### Testes
O arquivo `testes_automatizados.sh` contém uma pequena sequência de ações para exemplicar o funcionamento do sistema. 

## Retorno do Banco de Dados
O servidor retornará informações dependendo da operação solicitada. Solicitações que falharem receberão como retorno
a chave enviada, uma string vazia como valor e a versão setada como 0.

## Documentação do esquema de dados usados nas tabelas.
Para representar a base de dados dos servidores, utilizamos um dicionário do python.

As chaves passadas pelo cliente são as chaves do dicionário, e o conteúdo da chave do dicionário é um 
vetor de tuplas (valor, versão). Cada tupla contém uma string que é o valor fornecido pelo cliente e a versão atribuída pelo sistema.

Essa estrutura garante que cada chave estará relacionada com todas as versões e valores que já foram atribuídas a ela.

## Principais Dificuldade na Execução do Projeto
Encontramos dificuldades durante a utilização da biblioteca plyvel e a forma de utilizar os seus retornos. Além disso, foi um processo trabalhoso  adaptar as funções que utilizamos no servidor, na etapa anterior, para o Banco de Dados.
Como o pysyncobj não fornecia o serviço para comunicação externa, utilizamos Sockets para fazer a comunicação entre servidor e replicas.
Por falta de tempo, não lidamos com a possibilidade de haver cache no servidor
