
import grpc
import proto.projeto_pb2 as pp
import proto.projeto_pb2_grpc as ppg

import paho.mqtt.client as mqtt

import time
import argparse
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

def creating_arg_parser():
    parser = argparse.ArgumentParser(description='Servidor do sistema de armazenamento Chave-Valor Versionado.')
    parser.add_argument('--porta', nargs='?', default=40000, type=int, help='Porta onde o servidor irá ouvir')

    return parser

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
                return (chave,"",0)

            (val, ver) = busca_binaria_versao(valores, versao)
            return (chave, val, ver)

    def getRange(self, chave_ini, ver_ini, chave_fim, ver_fim):
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

        aux = max(chave_ini,chave_fim)
        chave_ini = min(chave_ini, chave_fim)
        chave_fim = aux

        ini = fim = 0
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
        for (chave, valor) in conjunto:
            retorno = self.put(chave,valor)
            resposta.append(retorno)

        return resposta

    def adicionar_entrada(self, chave, valor, versao):
        if chave not in self.__tabela:
            self.__tabela[chave] = [(valor,int(versao))]
        else:
            vetor = self.__tabela[chave]
            vetor.append((valor, int(versao)))
            self.__tabela[chave] = vetor

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
        for chave in conjunto:
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
    __banco = None
    __mqtt_client = None

    def __init__(self, banco, client):
        self.__banco = banco
        self.__mqtt_client = client

    def Get(self, request, context):
        (chave, valor, versao) = self.__banco.get(request.key, request.ver)
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def GetRange(self, request, context):
        fr = request.fr
        to = request.to
        resposta = self.__banco.getRange(fr.key, fr.ver, to.key, to.ver)

        for (chave,valor,versao) in resposta:
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def GetAll(self, request_iterator, context):
        vet = []
        for i in request_iterator:
            vet.append((i.key,i.ver))

        retorno = self.__banco.getAll(vet)
        for i in retorno:
            (chave, valor, ver) = i
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=ver)

    def Put(self, request, context):
        (chave,valor_ant,ver_ant,ver_atual) = self.__banco.put(request.key, request.val)

        self.__mqtt_client.publish("put",f"{id},{chave},{request.val},{ver_atual}")
        return pp.PutReply(key=chave,old_val=valor_ant,old_ver=ver_ant,ver=ver_atual)

    def PutAll(self, request_iterator, context):
        vet = []

        for i in request_iterator:
            vet.append((i.key, i.val))

        retorno = self.__banco.putAll(vet)

        versoes = []
        for (_,_,_,ver_atual) in retorno:
            versoes.append(ver_atual)

        publicar = f"{id}"
        for i in range(len(vet)):
            publicar += f",,({vet[i][0]},{vet[i][1]},{versoes[i]})"
        self.__mqtt_client.publish("putall",publicar)

        for i in retorno:
            (chave,valor_ant,ver_ant,ver) = i
            yield pp.PutReply(key=chave,old_val=valor_ant,old_ver=ver_ant,ver=ver)

    def Del(self, request, context):
        (chave,valor,versao) = self.__banco.dell(request.key)

        self.__mqtt_client.publish("del",f"{id},{chave}")
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def DelAll(self, request_iterator, context):
        vet = []
        for i in request_iterator:
            vet.append(i.key)

        retorno = self.__banco.dellAll(vet)

        publicar = f"{id}"
        for (chave,_,_) in retorno:
            publicar += f",{chave}"
        self.__mqtt_client.publish("delall",publicar)

        for i in retorno:
            (chave,valor,versao) = i
            yield pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

    def DelRange(self, request, context):
        fr = request.fr
        to = request.to
        resposta = self.__banco.dellRange(fr.key,to.key)

        self.__mqtt_client.publish("delrange",f"{id},{fr.key},{to.key}")

        for (chave, valor, versao) in resposta:
            yield pp.KeyValueVersionReply(key=chave, val=valor, ver=versao)

    def Trim(self, request, context):
        (chave,valor,versao) = self.__banco.trim(request.key)

        self.__mqtt_client.publish("trim", f"{id},{chave}")
        return pp.KeyValueVersionReply(key=chave,val=valor,ver=versao)

def on_message_put(client, userdata, message):
    # trata os dados recebidos no tópico put
    identificador, chave, valor, versao = message.payload.decode().split(",")
    if id != int(identificador):
        banco.adicionar_entrada(chave,valor,versao)
        print(f"Atualização da base de dados recebida.\n\tPUT: {chave} {valor} {versao}")

def on_message_putall(client, userdata, message):
    # tópico putall
    recebido = message.payload.decode().split(",,")
    identificador = recebido[0]
    if id != int(identificador):
        for i in recebido[1:]:
            (chave,valor,ver) = i.split(',')
            chave =  chave[1:]
            ver = int(ver[0:-1])

            banco.adicionar_entrada(chave,valor,ver)

        print(f"Atualização da base de dados recebida.\n\tPUTALL: ...")

def on_message_del(client, userdata, message):
    # trata os dados recebidos no tópico del

    identificador, chave = message.payload.decode().split(",")
    if id != int(identificador):
        banco.dell(chave)
        print(f"Atualização da base de dados recebida.\n\tDEL: {chave}")

def on_message_delrange(cliente, userdata, message):
    # trata os dados recebidos no tópico delrange

    identificador, chave_ini, chave_fim = message.payload.decode().split(",")
    if id != int(identificador):
        banco.dellRange(chave_ini, chave_fim)
        print(f"Atualização da base de dados recebida.\n\tDELRANGE: {min(chave_ini,chave_fim)} ... {max(chave_ini,chave_fim)}")

def on_message_delall(cliente, userdata, message):
    # tópico delall

    recebido = message.payload.decode().split(",")
    identificador = recebido[0]
    if id != int(identificador):
        banco.dellAll(recebido[1:])

        print(f"Atualização da base de dados recebida.\n\tDELALL: ...")


def on_message_trim(client, userdata, message):
    # trata os dados recebidos no tópico trim

    identificador, chave = message.payload.decode().split(',')
    if id != int(identificador):
        banco.trim(chave)
        print(f"Atualização da base de dados recebida.\n\tTRIM: {chave}")

def conectar_cliente():
    broker = 1883

    global id
    id = int(time.time() * 1000000)

    mqtt_client = mqtt.Client(f"{id}")  # criando cliente mqtt

    try:
        mqtt_client.connect("localhost", broker, 60)  # conectando com o broker
        print("Servidor conectado com o broker.")
    except Exception:
        print("Falha ao se conectar com o broker. Verifique se o broker está sendo executado.")
        exit()

    mqtt_client.subscribe("put")
    mqtt_client.subscribe("putall")
    mqtt_client.subscribe("del")
    mqtt_client.subscribe("delrange")
    mqtt_client.subscribe("delall")
    mqtt_client.subscribe("trim")

    mqtt_client.message_callback_add("put",on_message_put)
    mqtt_client.message_callback_add("putall",on_message_putall)
    mqtt_client.message_callback_add("del",on_message_del)
    mqtt_client.message_callback_add("delrange",on_message_delrange)
    mqtt_client.message_callback_add("delall",on_message_delall)
    mqtt_client.message_callback_add("trim",on_message_trim)

    return mqtt_client

def main():
    command_line = creating_arg_parser().parse_args()
    porta = str(command_line.porta)

    global banco
    banco = hashTable() # cria a base de dados do servidor
    mqtt_client = conectar_cliente() # cria o cliente mqtt

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ppg.add_KeyValueStoreServicer_to_server(KeyValueStore(banco,mqtt_client), server)
    try:
        mqtt_client.loop_start()

        server.add_insecure_port("[::]:" + porta)
        server.start()
        print(f"Servidor Iniciado, escutando na porta {porta}")

        server.wait_for_termination()
        mqtt_client.loop_stop()
    except RuntimeError:
        print(f"Não foi possível atribuir a porta {porta} ao servidor.")

if __name__ == "__main__":
    main()
