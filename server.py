import copy

import grpc
import projeto_pb2
import projeto_pb2_grpc as ppg

import sys
import time
from concurrent import futures

def tempo_em_milisec():
    return int(time.time() * 1000)

def busca_binaria(vetor, ver):
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

class hashTable:
    __tabela: {"": [("", int)]} = {}

    def get(self, chave, versao):
        if chave not in self.__tabela:
            raise Exception("Chave inexistente.")

        valores = self.__tabela.get(chave)

        if versao <= 0:
            # retornar versão mais recente

            (val, ver) = valores[-1]
            return (chave,val, ver)
        else:
            (_, ver_ant) = valores[0]
            if ver_ant > versao:
                raise Exception("Versão Inexistente.")

            (val, ver) = busca_binaria(valores, versao)
            return (chave, val, ver)

    def put(self, chave, valor):

        versao = tempo_em_milisec()
        if chave not in self.__tabela:
            # inserir nova chave
            self.__tabela["chave"] = [(valor,versao)]

            return [(chave,valor,versao)]
        else:
            # atualizar entrada
            vetor = self.__tabela.get(chave)
            (val_ant, ver_ant) = vetor[-1]
            vetor.append((valor, versao))
            self.__tabela[chave] = vetor

            return [(chave,val_ant,ver_ant),(chave,valor,versao)]

    def dell(self, chave):
        if chave not in self.__tabela:
            raise Exception("Chave Inexistente")

        vetor = self.__tabela.get(chave)
        recente = vetor[-1]
        self.__tabela.pop(chave)

        (val, ver) = recente
        return (chave, val, ver)


    def trim(self, chave):
        if chave not in self.__tabela:
            raise Exception("Chave Inexistente")

        vetor = self.__tabela.get(chave)
        recente = vetor[-1]
        self.__tabela[chave] = [recente]

        (val,ver) = recente
        return (chave,val,ver)


class KeyValueStore(ppg.KeyValueStoreServicer):

    def Get(self, request, context):
        print()

    def GetRange(self, request, context):
        print()

    def GetAll(self, request_iterator, context):
        print()

    def Put(self, request, context):
        print()

    def PutAll(self, request_iterator, context):
        print()

    def Del(self, request, context):
        print()

    def DelAll(self, request_iterator, context):
        print()

    def DelRange(self, request, context):
        print()

    def Trim(self, request, context):
        print()

def servidor(porta):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ppg.add_KeyValueStoreServicer_to_server(KeyValueStore(),server)

def main():
    n = len(sys.argv)  # qtd de argumentos

    if n != 2:
        print("Quantidade incorreta de argumentos.")
        return

    port = sys.argv[1]
    servidor(port)

if __name__ == "__main__":
    main()