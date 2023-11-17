import grpc

import proto.projeto_pb2 as pp
import proto.projeto_pb2_grpc as ppg

import time
import argparse
from concurrent import futures

import socket
import random


def tempo_em_milisec():
    return int(time.time() * 1000)

def creating_arg_parser():
    parser = argparse.ArgumentParser(description='Servidor do sistema de armazenamento Chave-Valor Versionado.')
    parser.add_argument('--porta', nargs='?', default=40000, type=int, help='Porta onde o servidor irá ouvir')

    return parser

class KeyValueStore(ppg.KeyValueStoreServicer):

    def Get(self, request, context):
        retorno = conectarBD()
        if not retorno:
            return pp.KeyValueVersionReply(key="",val="",ver=-1)

        requisicao = f"get:{request.key},{request.ver}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor,versao = data.decode().split(",")

        s.close()
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=int(versao))

    def GetRange(self, request, context):
        retorno = conectarBD()
        if not retorno:
            yield pp.KeyValueVersionReply(key="",val="",ver=-1)
        else:
            fr = request.fr
            to = request.to

            requisicao = f"getrange:{fr.key},{fr.ver};{to.key},{to.ver}"
            s.send(requisicao.encode())

            data = s.recv(1024)
            dados = data.decode().split(";")

            s.close()
            for i in dados:
                chave, valor, versao = i.split(",")

                yield pp.KeyValueVersionReply(key=chave, val=valor, ver=int(versao))

    def GetAll(self, request_iterator, context):
        retorno = conectarBD()
        if not retorno:
            yield pp.KeyValueVersionReply(key="",val="",ver=-1)
        else:
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

                yield pp.KeyValueVersionReply(key=chave,val=valor,ver=int(ver))

    def Put(self, request, context):
        retorno = conectarBD()
        if not retorno:
            return pp.PutReply(key="", old_val="", old_ver=-1, ver= -1)

        requisicao = f"put:{request.key},{request.val},{tempo_em_milisec()}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor_ant,ver_ant,ver_atual = data.decode().split(",")

        s.close()
        return pp.PutReply(key=chave,old_val=valor_ant,old_ver=int(ver_ant),ver=int(ver_atual))

    def PutAll(self, request_iterator, context):
        retorno = conectarBD()

        if not retorno:
            yield pp.PutReply(key="", old_val="", old_ver=-1, ver= -1)
        else:
            requisicao = "putall:"
            for i in request_iterator:
                requisicao += f"{i.key},{i.val},{tempo_em_milisec()};"

            requisicao = requisicao[0:-1]
            s.send(requisicao.encode())

            data = s.recv(1024)
            dados = data.decode().split(";")

            s.close()
            for i in dados:
                chave,valor_ant,ver_ant,ver = i.split(",")
                yield pp.PutReply(key=chave,old_val=valor_ant,old_ver=int(ver_ant),ver=int(ver))

    def Del(self, request, context):
        retorno = conectarBD()
        if not retorno:
            return pp.KeyValueVersionReply(key="",val="",ver=-1)

        requisicao = f"del:{request.key}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor,versao = data.decode().split(",")

        s.close()
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=int(versao))

    def DelAll(self, request_iterator, context):
        retorno = conectarBD()
        if not retorno:
            yield pp.KeyValueVersionReply(key="",val="",ver=-1)
        else:
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
                yield pp.KeyValueVersionReply(key=chave,val=valor,ver=int(versao))

    def DelRange(self, request, context):
        retorno = conectarBD()
        if not retorno:
            yield pp.KeyValueVersionReply(key="",val="",ver=-1)
        else:
            requisicao = f"delrange:{request.fr.key};{request.to.key}"

            s.send(requisicao.encode())

            data = s.recv(1024)
            dados = data.decode().split(";")

            s.close()
            for i in dados:
                chave, valor, versao = i.split(",")
                yield pp.KeyValueVersionReply(key=chave, val=valor, ver=int(versao))

    def Trim(self, request, context):
        retorno = conectarBD()
        if not retorno:
            return pp.KeyValueVersionReply(key="",val="",ver=-1)

        requisicao = f"trim:{request.key}"

        s.send(requisicao.encode())

        data = s.recv(1024)
        chave,valor,versao = data.decode().split(",")

        s.close()

        return pp.KeyValueVersionReply(key=chave,val=valor,ver=int(versao))

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
            print(f"Conectando-se ao banco de dados na porta {porta_bancos[escolha]}.")
            break
        except Exception as e:
            tentativas += 1
            print(f"Erro: {e}")

    if tentativas == 10:
        print(f'Foram realizadas {tentativas} tentativas fracassadas de conexão ao Banco de Dados. A requisição falhou.')
        return False
    else:
        return True

def main():
    command_line = creating_arg_parser().parse_args()
    porta = str(command_line.porta)

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