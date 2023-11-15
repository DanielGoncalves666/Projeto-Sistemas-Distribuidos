import argparse

import plyvel
from pysyncobj import SyncObj, replicated

import time
import socket

def busca_binaria_versao(vetor, ver):
    # caso a versão não exista, retorna a entrada imediatamente menor

    min = 0
    max = len(vetor) - 1
    media = (min + max) // 2

    [_, _, ver_atual] = vetor[-1]

    if ver > ver_atual:
        return vetor[-1]

    while True:
        [_,_,versao] = vetor[media]
        if versao == ver:
            return vetor[media]

        if versao < ver:
            min = media + 1
        elif versao > ver:
            max = media - 1

        if min > max:
            return vetor[media - 1]

        media = (min + max) // 2

class Database(SyncObj):

    def __init__(self, self_address, partners,):
        self.__db = plyvel.DB(f"DBs/{self_address}", create_if_missing=True)
        super(Database,self).__init__(self_address, partners)
        self.__mensagem = ""

    def get_retorno(self, chave, versao):
        prefixo = f"{chave}!"
        resultado = []
        for chave_composta, value in self.__db.iterator(start=prefixo.encode(), stop=(prefixo.encode() + b'~')):
            key, version = chave_composta.decode().split("!")
            resultado.append([key, value.decode(), int(version)])

        if len(resultado) == 0:  # chave inexistente
            return (chave,"",0)
        elif int(versao) <= 0:  # versão mais recente (key,value,version)
            return [resultado[-1][0],resultado[-1][1],resultado[-1][2]]
        else:
            if int(versao) < resultado[0][2]:  # versão menor que a menor versão armazenada
                return [chave,"",0]
            else:
                [_, val, ver] = busca_binaria_versao(resultado, int(versao))
                return [chave,val,ver]

    def get(self, chave, versao):

        prefixo = f"{chave}!"
        resultado = []
        for chave_composta, value in self.__db.iterator(start=prefixo.encode(), stop=(prefixo.encode() + b'~')):
            key, version = chave_composta.decode().split("!")
            resultado.append([key, value.decode(), int(version)])

        if len(resultado) == 0: # chave inexistente
            self.__mensagem = f"{chave},,{0}"
        elif int(versao) <= 0: # versão mais recente (key,value,version)
            self.__mensagem = f"{resultado[-1][0]},{resultado[-1][1]},{resultado[-1][2]}"
        else:
            if int(versao) < resultado[0][2]: # versão menor que a menor versão armazenada
                self.__mensagem = f"{chave},,{0}"
            else:
                [_, val, ver] = busca_binaria_versao(resultado,int(versao))
                self.__mensagem = f"{chave},{val},{ver}"

    def getRange(self, chave_ini, ver_ini, chave_fim, ver_fim):
        maior_ver = max(ver_ini, ver_fim)

        prefixo_ini = f"{chave_ini}"
        prefixo_fim = f"{chave_fim}"

        resultado = []
        atual = ""
        for chave_composta, value in self.__db.iterator(star=prefixo_ini.encode(), stop=(prefixo_fim.encode() + b'~')):
            key, version = chave_composta.decode().split("!")
            if atual == "" or atual == key:
                atual = key
                resultado.append([key, value.decode(), int(version)])
            elif atual != key:
                if int(maior_ver) <= 0:  # versão mais recente (key,value,version)
                    self.__mensagem += f"{resultado[-1][0]},{resultado[-1][1]},{resultado[-1][2]}:"
                else:
                    if int(maior_ver) < resultado[0][2]:  # versão menor que a menor versão armazenada
                        self.__mensagem += f"{atual},,{0}:"
                    else:
                        [_, val, ver] = busca_binaria_versao(resultado, int(maior_ver))
                        self.__mensagem += f"{atual},{val},{ver}:"

                resultado = []
                atual = key

        if len(resultado) == 0: # chave inexistente
            self.__mensagem = f"{chave_ini},,{0}:{chave_fim},,{0}"
        elif int(maior_ver) <= 0: # versão mais recente (key,value,version)
            self.__mensagem = f"{resultado[-1][0]},{resultado[-1][1]},{resultado[-1][2]}"
        else:
            if int(maior_ver) < resultado[0][2]: # versão menor que a menor versão armazenada
                self.__mensagem = f"{atual},,{0}"
            else:
                [_, val, ver] = busca_binaria_versao(resultado,int(maior_ver))
                self.__mensagem = f"{atual},{val},{ver}"

    def getAll(self, conjunto):
        buffer_mensagem = ""
        for i in range(len(conjunto)):
            (chave, versao) = conjunto[i]

            self.get(chave,versao)

            if i != 0:
                buffer_mensagem += ":"

            buffer_mensagem += self.__mensagem

        self.__mensagem = buffer_mensagem

    @replicated
    def put(self, chave, valor, versao):
        chave_final = chave + "!" + str(versao)

        key, val, ver = self.get_retorno(chave,0)

        self.__db.put(chave_final, valor)
        if ver == 0: # sem chave antiga
            self.__mensagem = f"{chave},,{0},{versao}"
        else:
            self.__mensagem = f"{chave},{val},{ver},{versao}"

    @replicated
    def putAll(self, conjunto):
        buffer_mensagem = ""

        for i in range(len(conjunto)):
            (chave,valor,versao) = conjunto[i]

            chave_final = chave + "!" + str(versao)

            key, val, ver = self.get_retorno(chave, 0)
            self.put(chave_final, valor)

            if ver == 0:  # sem chave antiga
                self.__mensagem = f"{chave},,{0},{versao}"
            else:
                self.__mensagem = f"{chave},{val},{ver},{versao}"

            if i != 0:
                buffer_mensagem += ":"

            buffer_mensagem += self.__mensagem

        self.__mensagem = buffer_mensagem

    @replicated
    def dell(self, chave):
        key, val, ver = self.get_retorno(chave,0)

        if ver == 0:
            self.__mensagem = f"{chave},,{0}"
        else:
            self.__mensagem = f"{chave},{val},{ver}"

            prefixo = f"{chave}!"
            resultado = []
            for chave_composta, _ in self.__db.iterator(start=prefixo.encode(), stop=(prefixo.encode() + b'~')):
                resultado.append(chave_composta)

            for i in resultado:
                self.__db.delete(i)


    def dellRange(self,chave_ini, chave_fim):
        prefixo_ini = f"{chave_ini}"
        prefixo_fim = f"{chave_fim}"

        resultado = []
        atual = ""
        for chave_composta, value in self.__db.iterator(start=prefixo_ini.encode(), stop=(prefixo_fim.encode() + b'~')):
            key, version = chave_composta.decode().split("!")
            if atual == "" or atual == key:
                atual = key
                anterior = [key, value.decode(), int(version)]
                resultado.append(chave_composta)
            elif atual != key:
                self.__mensagem += f"{anterior[0]},{anterior[1]},{anterior[2]}:"
                atual = key
                anterior = [key, value.decode(), int(version)]
                resultado.append(chave_composta)

        if len(resultado) == 0: # chave inexistente
            self.__mensagem += f"{chave_ini},,{0}:{chave_fim},,{0}"
        else:
            self.__mensagem += f"{anterior[0]},{anterior[1]},{anterior[2]}"

        for i in resultado:
            self.__db.delete(i)

    def dellAll(self, conjunto):
        buffer_mensagem = ""

        for i in range(len(conjunto)):
            chave = conjunto[i]

            key, val, ver = self.get_retorno(chave, 0)

            if ver != 0:
                for chave_composta, _ in self.__db.iterator(start=chave.encode(),
                                                                stop=(chave.encode() + b'~')):
                    self.__db.delete(chave_composta)

            if ver == 0:  # sem chave
                self.__mensagem = f"{chave},,{0}"
            else:
                self.__mensagem = f"{chave},{val},{ver}"

            if i != 0:
                buffer_mensagem += ":"

            buffer_mensagem += self.__mensagem

        self.__mensagem = buffer_mensagem

    def trim(self, chave):
        key, val, ver = self.get_retorno(chave,0)

        if ver == 0:
            self.__mensagem = f"{chave},,{0}"
        else:
            for chave_composta, _ in self.__db.iterator(start=chave.encode(),
                                                        stop=(chave.encode() + b'~')):
                key, version = chave_composta.decode().split("!")

                if version != ver:
                    self.__db.delete(chave_composta)

            self.__mensagem = f"{chave},{val},{ver}"

    def get_mensagem(self):
        time.sleep(1)

        retorno = self.__mensagem
        self.__mensagem = ""

        return retorno

    def set_mensagem(self, mensagem):
        self.__mensagem = mensagem

def creating_arg_parser():
    parser = argparse.ArgumentParser(description='Réplica do Banco de Dados do sistema de armazenamento Chave-Valor Versionado.')
    parser.add_argument('banco', default="bd1" ,help='Réplica que deve ser iniciada.')

    return parser

def bind2port(porta):
    global s

    try:
        s = socket.socket()
        host = socket.gethostname()
        s.bind((host,porta))
        s.listen(1)

    except Exception as e:
        print(f"Erro: {e}")
        exit(0)


def main():
    command_line = creating_arg_parser().parse_args()

    banco = command_line.banco
    if banco != "bd1" and banco != "bd2" and banco != "bd3":
        print("Réplica inválida!")
        exit(0)

    partners = ["127.0.0.1:10001", "127.0.0.1:10002", "127.0.0.1:10003"]

    if banco == "bd1":
        self_address = "127.0.0.1:10001"
        partners.remove("127.0.0.1:10001")
        porta = 20001
    elif banco == "bd2":
        self_address = "127.0.0.1:10002"
        partners.remove("127.0.0.1:10002")
        porta = 20002
    else:
        self_address = "127.0.0.1:10003"
        partners.remove("127.0.0.1:10003")
        porta = 20003


    BD = Database(self_address, partners)
    bind2port(porta)

    if banco == "bd1":
        BD.put("aaa","11","11")
        BD.put("aaa","14","14")
        BD.put("aaa","16","16")
        BD.put("aaa","20","20")
        BD.put("aaa","30","30")

    while True:
        c, addr = s.accept()

        data = c.recv(1024) # requisição do cliente

        thread_source, requisicao = data.decode().split("!")
        op, entrada = requisicao.split(":")

        if op == "get":
            (chave,versao) = entrada.split(",")
            BD.get(chave, versao)
        elif op == "getall":
            argumentos = []
            for i in entrada.split(";"):
                chave,versao = i.split(",")
                argumentos.append((chave,versao))

            BD.getAll(argumentos)
        elif op == "getrange":
            ini, fim = entrada.splot(";")
            chave_ini, ver_ini = ini.split(",")
            chave_fim, ver_fim = fim.split(",")

            BD.getRange(chave_ini, ver_ini, chave_fim, ver_fim)
        elif op == "put":
            chave,valor,versao = entrada.split(",")
            BD.put(chave,valor,versao)
        elif op == "putall":
            argumentos = []
            for i in entrada.split(";"):
                chave, valor, versao = i.split(",")
                argumentos.append((chave, valor, versao))

            BD.putAll(argumentos)
        elif op == "del":
            BD.dell(entrada)
        elif op == "delall":
            argumentos = []
            for i in entrada.split(";"):
                argumentos.append(i)

            BD.dellAll(argumentos)
        elif op == "delrange":
            ini, fim = entrada.split(";")
            BD.dellRange(ini,fim)
        elif op == "trim":
            BD.trim(entrada)
        else:
            BD.set_mensagem("Operação Inválida")


        c.send(BD.get_mensagem().encode())

        c.close()

if __name__ == "__main__":
    main()