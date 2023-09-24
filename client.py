import grpc
import projeto_pb2 as pp
import projeto_pb2_grpc as ppg

import argparse

def create_KeyRequest(chave, ver):
    return pp.KeyRequest(key=chave, ver=ver)

def create_KeyRange(chave_ini, ver_ini, chave_fim, ver_fim):
    inicio = create_KeyRequest(chave_ini,ver_ini)
    fim = create_KeyRequest(chave_fim,ver_fim)
    return pp.KeyRange(fr=inicio, to=fim)

def create_KeyValueRequest(chave, valor):
    return pp.KeyValueRequest(key=chave,val=valor)

def create_getAll_generator(chaves, qtd_chaves, versoes, qtd_versoes):
    for i in range(qtd_chaves):
        key = chaves[i]
        ver = 0 if i >= qtd_versoes else versoes[i]
        yield create_KeyRequest(key, ver)

def create_putAll_generator(chaves, qtd_chaves, valores):
    for i in range(qtd_chaves):
        key = chaves[i]
        val = valores[i]
        yield create_KeyValueRequest(key, val)

def create_delall_generator(chaves, qtd_chaves):
    for i in range(qtd_chaves):
        key = chaves[i]
        yield create_KeyRequest(key, 0)

def creating_arg_parser():
    comandos_possiveis = ['get', 'getrange', 'getall', 'put', 'putall', 'del', 'delrange', 'delall', 'trim']

    # a instância de ArgumentParser irá conter todas as informações da interface de linha de comando
    parser = argparse.ArgumentParser(description='Cliente de acesso ao sistema de armazenamento Chave-Valor Versionado.')
    # add_argument adiciona argumentos que podem ser inseridos na linha de comando
    parser.add_argument('--porta', nargs='?', default=40000, type=int, help='Porta do servidor para conexão.')
    parser.add_argument('op', choices=comandos_possiveis, help="Operação a ser realizada.")
    parser.add_argument('--chave', nargs='+', required=True, help="Chave(s) na(s) qual(is) a operação será aplicada.")
    parser.add_argument('--valor', nargs='+', help="Novo(s) Valor(es) para a(s) chave(s) especificada(s).")
    parser.add_argument('--versao', nargs='+', type=int, help="Versão(ões) da(s) chave(s) especificada(s) que se deseja.")

    return parser

def Client(porta, op, chaves, valores, versoes):
    with grpc.insecure_channel("[::]:" + porta) as channel:
        stub = ppg.KeyValueStoreStub(channel)

        qtd_chaves = len(chaves)
        qtd_valores = len(valores)
        qtd_versoes = len(versoes)

        resposta = []
        erro = 0
        if op == "get":
            if qtd_chaves != 1:
                print(f"{op}: Esperava-se {1} chave(s), {qtd_chaves} chave(s) foram passadas.")
                erro += 1

            if qtd_valores != 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 1:
                print(f"{op}: Esperava-se no máximo 1 versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            key = chaves[0]
            ver = 0 if versoes == [] else versoes[0]
            resposta = stub.Get(create_KeyRequest(key, ver))

        elif op == "getrange":
            if qtd_chaves != 2:
                print(f"{op}: Esperava-se {2} chave(s), {qtd_chaves} chave(s) foram passadas.")
                erro += 1

            if qtd_valores != 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 2:
                print(f"{op}: Esperava-se no máximo 2 versões, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            key_ini = chaves[0]
            key_fim = chaves[1]
            if len(versoes) == 0:
                ver_ini = ver_fim = 0
            elif len(versoes) == 1:
                ver_ini = versoes[0]
                ver_fim = 0
            else:
                ver_ini = versoes[0]
                ver_fim = versoes[1]

            resposta = []
            for r in stub.GetRange(create_KeyRange(key_ini, ver_ini, key_fim, ver_fim)):
                resposta.append(r)

        elif op == "getall":
            if qtd_valores != 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > qtd_chaves:
                print(f"{op}: Esperava-se no máximo {qtd_chaves} versões, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            gen = create_getAll_generator(chaves, qtd_chaves, versoes, qtd_versoes)
            for r in stub.GetAll(gen):
                resposta.append(r)

        elif op == "put":
            if qtd_chaves != 1:
                print(f"{op}: Esperava-se {1} chave(s), {qtd_chaves} chave(s) foram passadas.")
                erro += 1

            if qtd_valores != 1:
                print(f"{op}: Esperava-se {1} valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 0:
                print(f"{op}: Esperava-se nenhuma versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            key = chaves[0]
            val = valores[0]

            resposta = stub.Put(create_KeyValueRequest(key, val))

        elif op == "putall":
            if qtd_valores != qtd_chaves:
                print(f"{op}: Esperava-se {qtd_chaves} valor(es), {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 0:
                print(f"{op}: Esperava-se nenhuma versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            gen = create_putAll_generator(chaves, qtd_chaves, valores)
            for r in stub.PutAll(gen):
                resposta.append(r)

        elif op == "del":
            if qtd_chaves != 1:
                print(f"{op}: Esperava-se {1} chave, {qtd_chaves} chave(s) foram passadas.")
                erro += 1

            if qtd_valores > 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 0:
                print(f"{op}: Esperava-se nenhuma versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            key = chaves[0]
            resposta = stub.Del(create_KeyRequest(key, 0))

        elif op == "delrange":
            if qtd_chaves != 2:
                print(f"{op}: Esperava-se {2} chave(s), {qtd_chaves} chave(s) foram passadas.")
                erro += 1

            if qtd_valores > 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 0:
                print(f"{op}: Esperava-se no nenhuma versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            key_ini = chaves[0]
            key_fim = chaves[1]

            resposta = []
            for r in stub.DelRange(create_KeyRange(key_ini, 0, key_fim, 0)):
                resposta.append(r)

        elif op == "delall":
            if qtd_valores > 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 0:
                print(f"{op}: Esperava-se nenhuma versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            gen = create_delall_generator(chaves, qtd_chaves)

            resposta = []
            for r in stub.DelAll(gen):
                resposta.append(r)

        elif op == "trim":
            if qtd_chaves != 1:
                print(f"{op}: Esperava-se {1} chave, {qtd_chaves} chave(s) foram passadas.")
                erro += 1

            if qtd_valores > 0:
                print(f"{op}: Esperava-se nenhum valor, {qtd_valores} valor(es) foram passados.")
                erro += 1

            if qtd_versoes > 0:
                print(f"{op}: Esperava-se nenhuma versão, {qtd_versoes} versoes foram passadas.")
                erro += 1

            if erro > 0:
                exit()

            key = chaves[0]
            resposta = stub.Trim(create_KeyRequest(key, 0))

        return resposta

def main():
    # parse_args cria os objetos referentes ao que foi passado na linha de comando
    command_line = creating_arg_parser().parse_args()

    porta = str(command_line.porta)
    op = command_line.op
    chaves = command_line.chave
    valores = [] if command_line.valor == None else command_line.valor
    versoes = [] if command_line.versao == None else command_line.versao

    retorno = Client(porta,op,chaves,valores,versoes)
    print(f"{retorno}")

if __name__ == "__main__":
    main()