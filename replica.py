import argparse

import plyvel
from pysyncobj import SyncObj, replicated

import time

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


    @replicated
    def put(self, chave, valor, versao):
        chave_final = chave + "!" + str(versao)
        self.__db.put(chave_final.encode(), valor.encode())

    @replicated
    def get(self, chave, versao):
        mensagem = ""

        prefixo = f"{chave}!"
        resultado = []
        for chave_composta, value in self.__db.iterator(start=prefixo.encode(), stop=(prefixo.encode() + b'~')):
            key, version = chave_composta.decode().split("!")
            resultado.append([key, value.decode(), int(version)])

        if len(resultado) == 0: # chave inexistente
            mensagem = f"{chave},,{0}"
        elif int(versao) <= 0: # versão mais recente (key,value,version)
            mensagem = f"{resultado[-1][0]},{resultado[-1][1]},{resultado[-1][2]}"
        else:
            if int(versao) < resultado[0][2]: # versão menor que a menor versão armazenada
                mensagem = f"{chave},,{0}"
            else:
                [_, val, ver] = busca_binaria_versao(resultado,int(versao))
                mensagem = f"{chave},{val},{ver}"

        print(mensagem)

def creating_arg_parser():
    parser = argparse.ArgumentParser(description='Réplica do Banco de Dados do sistema de armazenamento Chave-Valor Versionado.')
    parser.add_argument('banco', default="bd1" ,help='Réplica que deve ser iniciada.')

    return parser
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
    elif banco == "bd2":
        self_address = "127.0.0.1:10002"
        partners.remove("127.0.0.1:10002")
    else:
        self_address = "127.0.0.1:10003"
        partners.remove("127.0.0.1:10003")



    BD = Database(self_address, partners)

    if banco == "bd1":
        BD.put("aaa","11","11")
        BD.put("aaa","14","14")
        BD.put("aaa","16","16")
        BD.put("aaa","20","20")
        BD.put("aaa","30","30")

    while True:
        if banco == "bd2":
            BD.get("aaa","11")
            BD.get("aaa","12")
            BD.get("aaa","10")
            BD.get("bbb","1")
        time.sleep(30)



if __name__ == "__main__":
    main()