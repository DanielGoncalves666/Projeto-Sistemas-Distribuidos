import grpc
import projeto_pb2 as pp
import projeto_pb2_grpc as ppg

import sys
import time
from concurrent import futures

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

class hashTable:
    __tabela: {"": [("", int)]} = {}

    def get(self, chave, versao):
        if chave not in self.__tabela:
            return (chave,"",0)

        valores = self.__tabela.get(chave)

        if versao <= 0:
            # retornar versão mais recente

            (val, ver) = valores[-1]
            return (chave,val, ver)
        else:
            (_, ver_ant) = valores[0]
            if ver_ant > versao:
                return (chave,"",versao)

            (val, ver) = busca_binaria_versao(valores, versao)
            return (chave, val, ver)

    def getRange(self,chave_ini, chave_fim, ver_ini, ver_fim):
        intervalo_chaves = self.__determinar_intervalo_chaves(chave_ini,chave_fim)
        maior_versao = max(ver_fim,ver_ini)

        resposta = []

        for i in intervalo_chaves:
            retorno = self.get(i,maior_versao)
            resposta.append(retorno)

        return resposta

    def __determinar_intervalo_chaves(self, chave_ini, chave_fim):
        todas_chaves = list(self.__tabela)
        todas_chaves.sort()

        # E SE AS CHAVES ESTIVEREM INVERTIDAS?
        # !!!!!!!!!!!!!
        for i in range(len(todas_chaves)):
            if todas_chaves[i] >= chave_ini:
                ini = i
                break

        for i in range(len(todas_chaves) - 1, -1, -1):
            if todas_chaves[i] <= chave_fim:
                fim = i
                break

        return todas_chaves[ini:fim + 1]


    def getAll(self, conjunto):
        resposta = []
        for (chave, versao) in conjunto:
            retorno = self.get(chave,versao)
            resposta.append(retorno)

        return resposta


    def put(self, chave, valor):

        versao = tempo_em_milisec()
        if chave not in self.__tabela:
            # inserir nova chave
            self.__tabela[chave] = [(valor,versao)]

            # chave, valor_antigo, ver_antiga, versao_nova
            return (chave,"",0,versao)
        else:
            # atualizar entrada
            vetor = self.__tabela.get(chave)
            (val_ant, ver_ant) = vetor[-1]
            vetor.append((valor, versao))
            self.__tabela[chave] = vetor

            return (chave,val_ant,ver_ant,versao)

    def putAll(self, conjunto):
        resposta = []
        for i in conjunto:
            chave = i.key
            valor = i.val
            retorno = self.put(chave,valor)
            resposta.append(retorno)

        return resposta

    def dell(self, chave):
        if chave not in self.__tabela:
            return (chave,"",0)

        vetor = self.__tabela.get(chave)
        recente = vetor[-1]
        self.__tabela.pop(chave)

        (val, ver) = recente
        return (chave, val, ver)

    def dellRange(self,chave_ini, chave_fim):
        intervalo_chaves = self.__determinar_intervalo_chaves(chave_ini,chave_fim)

        resposta = []
        for i in intervalo_chaves:
            retorno = self.dell(i)
            resposta.append(retorno)

        return resposta

    def dellAll(self, conjunto):
        resposta = []
        for i in conjunto:
            chave = i.key
            retorno = self.dell(chave)
            resposta.append(retorno)

        return resposta

    def trim(self, chave):
        if chave not in self.__tabela:
            return (chave,"",0)

        vetor = self.__tabela.get(chave)
        recente = vetor[-1]
        self.__tabela[chave] = [recente]

        (val,ver) = recente
        return (chave,val,ver)

    def imprimir_tabela(self):
        for (chave,vet) in self.__tabela.items():
            print(f"{chave} :")
            for (valor, ver) in vet:
                print(f"({valor},{ver})",end="")
            print()

class KeyValueStore(ppg.KeyValueStoreServicer):
    __banco = hashTable()

    def Get(self, request, context):
        (chave, valor, versao) = self.__banco.get(request.chave, request.versao)
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def GetRange(self, request, context):
        fr = request.fr
        to = request.to
        resposta = self.__banco.getRange(fr.key, fr.ver, to.key, to.ver)

        for (chave,valor,versao) in resposta:
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def GetAll(self, request_iterator, context):
        retorno = self.__banco.getAll(request_iterator)
        for i in retorno:
            (chave, valor, ver) = i
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=ver)

    def Put(self, request, context):
        (chave,valor_ant,ver_ant,ver_atual) = self.__banco.put(request.chave, request.valor)
        return pp.PutReply(key=chave,old_val=valor_ant,old_ver=ver_ant,ver=ver_atual)

    def PutAll(self, request_iterator, context):
        retorno = self.__banco.putAll(request_iterator)
        for i in retorno:
            (chave,valor_ant,ver_ant,ver) = i
            yield pp.PutReply(key=chave,old_val=valor_ant,old_ver=ver_ant,ver=ver)

    def Del(self, request, context):
        (chave,valor,versao) = self.__banco.dell(request.chave)
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def DelAll(self, request_iterator, context):
        retorno = self.__banco.dellAll(request_iterator)
        for i in retorno:
            (chave,valor,versao) = i
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def DelRange(self, request, context):
        fr = request.fr
        to = request.to
        resposta = self.__banco.dellRange(fr.key,to.key)

        for (chave, valor, versao) in resposta:
            yield pp.KeyValueVersionReply(key=chave, val=valor, ver=versao)

    def Trim(self, request, context):
        (chave,valor,versao) = self.__banco.trim(request.chave)
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

def servidor(porta):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ppg.add_KeyValueStoreServicer_to_server(KeyValueStore(),server)
    server.add_insecure_port("[::]:" + porta)
    server.start()
    print(f"Servidor Iniciado, escutando na porta {porta}")
    server.wait_for_termination()

def main():
    n = len(sys.argv)  # qtd de argumentos

    if n != 2:
        print("Quantidade incorreta de argumentos.")
        return

    port = sys.argv[1]
    servidor(port)

if __name__ == "__main__":
    main()