import grpc
import projeto_pb2
import projeto_pb2_grpc

import sys
from concurrent import futures

class KeyValueStore(projeto_pb2_grpc.KeyValueStoreServicer):

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
    projeto_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStore(),server)

def main():
    n = len(sys.argv)  # qtd de argumentos
    print(n)
    if n != 2:
        print("Quantidade incorreta de argumentos.")
        return

    port = sys.argv[1]
    servidor(port)

if __name__ == "__main__":
    main()