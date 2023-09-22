import grpc
import projeto_pb2
import projeto_pb2_grpc

import sys
import argparse

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
        print()


if __name__ == "__main__":
    main()