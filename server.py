import grpc

import projeto_pb2 as pp
import projeto_pb2_grpc as ppg

import time
import argparse
from concurrent import futures

import socket
import random


def tempo_em_milisec():
    return int(time.time() * 1000)

def busca_binaria_versao(vetor, ver):
    # caso a versão não exista, retorna a entrada imediatamente menor

    min = 0
    max = len(vetor) - 1
    media = (min + max) // 2

    (_, ver_atual) = vetor[-1]

    if ver > ver_atual:
        return vetor[-1]

    while True:
        (_,versao) = vetor[media]
        if versao == ver:
            return vetor[media]

        if versao < ver:
            min = media + 1
        elif versao > ver:
            max = media - 1

        if min > max:
            return vetor[media - 1]

        media = (min + max) // 2

def creating_arg_parser():
    parser = argparse.ArgumentParser(description='Servidor do sistema de armazenamento Chave-Valor Versionado.')
    parser.add_argument('--porta', nargs='?', default=40000, type=int, help='Porta onde o servidor irá ouvir')

    return parser

class KeyValueStore(ppg.KeyValueStoreServicer):

    def Get(self, request, context):
        conectarBD()

        requisicao = f"get:{request.key},{request.ver}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        dados = data.decode().split(",")
        chave = dados[0]
        valor = dados[1]
        versao = int(dados[2])

        s.close()
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def GetRange(self, request, context):
        conectarBD()

        fr = request.fr
        to = request.to

        requisicao = f"getrange:{fr.key},{fr.ver};{to.key},{to.ver}"
        s.send(requisicao.encode())

        data = s.recv(1024)
        dados = data.decode().split(";")

        s.close()
        for i in dados:
            chave, valor, versao = i.split(",")
            versao = int(versao)

            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def GetAll(self, request_iterator, context):
        conectarBD()

        requisicao = 'getall:'
        for i in request_iterator:
            requisicao += f"{i.key},{i.ver};"

        requisicao = requisicao[0:-1]
        s.send(requisicao.encode())

        data = s.recv(1024)
        dados = data.decode().split(";")

        s.close()
        for i in dados:
            chave, valor, ver = i.split(",")
            ver = int(ver)

            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=ver)

    def Put(self, request, context):
        conectarBD()

        requisicao = f"put:{request.key},{request.val}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor_ant,ver_ant,ver_atual = data.decode().split(",")

        s.close()
        return pp.PutReply(key=chave,old_val=valor_ant,old_ver=ver_ant,ver=ver_atual)

    def PutAll(self, request_iterator, context):
        conectarBD()

        requisicao = "putall:"
        for i in request_iterator:
            requisicao += f"{i.key},{i.val};"

        requisicao = requisicao[0:-1]
        s.send(requisicao.encode())

        data = s.recv(1024)
        dados = data.decode().split(";")

        s.close()
        for i in dados:
            chave,valor_ant,ver_ant,ver = i.split(",")
            yield pp.PutReply(key=chave,old_val=valor_ant,old_ver=ver_ant,ver=ver)

    def Del(self, request, context):
        conectarBD()

        requisicao = f"del:{request.key}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor,versao = data.decode().split(",")

        s.close()
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def DelAll(self, request_iterator, context):
        conectarBD()

        requisicao = "delall:"
        for i in request_iterator:
            requisicao += f"{i.key};"

        requisicao = requisicao[0:-1]
        s.send(requisicao.encode())

        data = s.recv(1024)
        dados = data.decode().split(";")

        s.close()
        for i in dados:
            chave,valor,versao = i.split(",")
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def DelRange(self, request, context):
        conectarBD()

        requisicao = f"delrange:{request.fr.key};{request.to.key}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        dados = data.decode().split(";")

        s.close()
        for i in dados:
            chave, valor, versao = i.split(",")
            yield pp.KeyValueVersionReply(key=chave, val=valor, ver=versao)

    def Trim(self, request, context):
        conectarBD()

        requisicao = f"trim:{request.key}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor,versao = data.decode().split(";")

        s.close()

        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

def conectarBD():
    global s
    porta_bancos = [20001,20002,20003]

    tentativas = 0
    while tentativas < 10:
        escolha = random.randint(0, 2)

        try:
            s = socket.socket()
            host = socket.gethostname()
            s.connect((host,porta_bancos[escolha]))
            break
        except Exception as e:
            tentativas += 1
            print(f"Erro: {e}")

    if tentativas == 10:
        print(f'Foram realizadas {tentativas} tentativas de conexão ao Banco de Dados sem sucesso. Finalizando...')
        exit(0)

def main():
    command_line = creating_arg_parser().parse_args()
    porta = str(command_line.porta)

    #global banco
    #banco = hashTable() # cria a base de dados do servidor

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ppg.add_KeyValueStoreServicer_to_server(KeyValueStore(), server)

    try:
        server.add_insecure_port("[::]:" + porta)
        server.start()
        print(f"Servidor Iniciado, escutando na porta {porta}")

        server.wait_for_termination()
    except RuntimeError:
        print(f"Não foi possível atribuir a porta {porta} ao servidor.")

if __name__ == "__main__":
    main()