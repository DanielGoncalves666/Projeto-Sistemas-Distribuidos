import grpc
import projeto_pb2 as pp
import projeto_pb2_grpc as ppg

import argparse

def create_KeyRequest(chave, ver):
    return pp.KeyRequest(key=chave, ver=ver)

def create_Keyrange(chave_ini, ver_ini, chave_fim, ver_fim):
    inicio = create_KeyRequest(chave_ini,ver_ini)
    fim = create_KeyRequest(chave_fim,ver_fim)
    return pp.KeyRange(fr=inicio, to=fim)

def create_KeyValueRequest(chave, valor):
    return pp.KeyValueRequest(key=chave,val=valor)

def creating_arg_parser():
    comandos_possiveis = ['get', 'getrange', 'getall', 'put', 'putall', 'del', 'delrange', 'delall', 'trim']

    # a instância de ArgumentParser irá conter todas as informações da interface de linha de comando
    parser = argparse.ArgumentParser(description='Cliente de acesso ao sistema de armazenamento Chave-Valor Versionado.')
    # add_argument adiciona argumentos que podem ser inseridos na linha de comando
    parser.add_argument('--porta', nargs='?', default=50000, type=int, help='Porta do servidor para conexão.')
    parser.add_argument('op', choices=comandos_possiveis, help="Operação a ser realizada.")
    parser.add_argument('chave', nargs='+', help="Chave(s) na(s) qual(is) a operação será aplicada.")
    parser.add_argument('-val', nargs='+', help="Novo(s) Valor(es) para a(s) chave(s) especificada(s).")
    parser.add_argument('-ver', nargs='+', type=int, help="Versão(ões) da(s) chave(s) especificada(s) que se deseja.")

    return parser

def main():
    # parse_args cria os objetos referentes ao que foi passado na linha de comando
    command_line = creating_arg_parser().parse_args()

    porta = str(command_line.porta)
    with grpc.insecure_channel("[::]:" + porta) as channel:
        stub = ppg.KeyValueStoreStub(channel)

        op = command_line.op
        chaves = command_line.chave
        qtd_chaves = len(chaves)
        valores = [] if command_line.val == None else command_line.val
        qtd_valores = len(valores)
        versoes = [] if command_line.ver == None else command_line.ver
        qtd_versoes = len(versoes)

        if op == "get":
            if qtd_chaves != 1 or qtd_valores != 0 or qtd_versoes > 1:
                print(f"{op}:\t Esperava-se {1} chave(s), {qtd_chaves} foram passadas. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} ou {1} versao(oes), {qtd_versoes} foram passadas.")
            else:
                key = chaves[0]
                ver = 0 if versoes == [] else versoes[0]
                resposta = stub.Get(create_KeyRequest(key,ver))

        elif op == "getrange":
            if qtd_chaves != 2 or qtd_valores != 0 or qtd_versoes > 2:
                print(f"{op}:\t Esperava-se {2} chave(s), {qtd_chaves} foram passadas. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0},{1} ou {2} versao(oes), {qtd_versoes} foram passadas.")
            else:
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
                for r in stub.GetRange(create_Keyrange(key_ini,ver_ini,key_fim,ver_fim)):
                    resposta.append(r)

        elif op == "getall":
            if qtd_versoes > qtd_chaves or qtd_valores != 0:
                print(f"{op}:\t Quantidade ilimitada de chaves permitida. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se no máximo {qtd_chaves} versoes, {qtd_versoes} foram passadas.")
            else:
                request = []
                for i in range(qtd_chaves):
                    key = chaves[i]
                    ver = 0 if i >= qtd_versoes else versoes[i]
                    request.append(create_KeyRequest(key,ver))

                resposta = []
                for r in stub.GetAll(request):
                    resposta.append(r)

        elif op == "put":
            if qtd_chaves != 1 or qtd_valores != 1 or qtd_versoes > 0:
                print(f"{op}:\t Esperava-se {1} chave(s), {qtd_chaves} foram passadas. \n"
                      f"\t Esperava-se {1} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} versao(oes), {qtd_versoes} foram passadas.")
            else:
                key = chaves[0]
                val = valores[0]

                resposta = stub.Put(create_KeyValueRequest(key,val))

        elif op == "putall":
            if qtd_chaves != qtd_valores or qtd_versoes > 0:
                print(f"{op}:\t Quantidade ilimitada de chaves permitida. \n"
                      f"\t Esperava-se {qtd_chaves} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} versoes, {qtd_versoes} foram passadas.")
            else:
                request = []
                for i in range(qtd_chaves):
                    key = chaves[i]
                    val = valores[i]
                    request.append(create_KeyValueRequest(key,val))

                resposta = []
                for r in stub.PutAll(request):
                    resposta.append(r)

        elif op == "del":
            if qtd_chaves != 1 or qtd_valores > 0 or qtd_versoes > 0:
                print(f"{op}:\t Esperava-se {1} chave(s), {qtd_chaves} foram passadas. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} versao(oes), {qtd_versoes} foram passadas.")
            else:
                key = chaves[0]

                resposta = stub.Del(create_KeyRequest(key,0))

        elif op == "delrange":
            if qtd_chaves != 2 or qtd_valores > 0 or qtd_versoes > 0:
                print(f"{op}:\t Esperava-se {2} chave(s), {qtd_chaves} foram passadas. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} versao(oes), {qtd_versoes} foram passadas.")
            else:
                key_ini = chaves[0]
                key_fim = chaves[1]

                resposta = []
                for r in stub.DelAll(create_Keyrange(key_ini,0,key_fim,0)):
                    resposta.app(r)

        elif op == "delall":
            if qtd_valores > 0 or qtd_versoes > 0:
                print(f"{op}:\t Quantidade ilimitada de chaves permitida. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} versao(oes), {qtd_versoes} foram passadas.")
            else:
                request = []
                for i in range(qtd_chaves):
                    key = chaves[i]
                    request.append(create_KeyRequest(key,0))

                resposta = []
                for r in stub.PutAll(request):
                    resposta.append(r)

        elif op == "trim":
            if qtd_chaves != 1 or qtd_valores != 0 or qtd_versoes != 0:
                print(f"{op}:\t Esperava-se {1} chave(s), {qtd_chaves} foram passadas. \n"
                      f"\t Esperava-se {0} valor(es), {qtd_valores} foram passados. \n"
                      f"\t Esperava-se {0} versao(oes), {qtd_versoes} foram passadas.")
            else:
                key = chaves[0]

                resposta = stub.Trim(create_KeyRequest(key,0))

        print(f"Resposta = {resposta}")

if __name__ == "__main__":
    main()