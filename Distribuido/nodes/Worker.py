# socket usado -> (AF_INET, SOCK_STREAM, IPPROTO_TCP)
# fluxo para serializar e desserializar a grade na hora do envio:
#
#	Servidor transforma a grade em bytes por meio do módulo "pickle"
# 
#	Servidor calcula o tamanho total em bytes da grade serializada. 
#	Isso seria feito armazenando a grade serializada em uma variável
#	e depois medindo o tamanho com len(var)
#
#	Após o cálculo e armazenamento do tamanho, o servidor usa o módu-
#	lo "struct" para transformar esse valor em bytes. Assim, o servidor
#	envia ao determinado nó o tamanho da grade que será enviada, antes
#	de enviar a grade em si.
#
#	Após o envio do tamanho da grade, o servidor envia a própria grade.


#	Do lado do nó worker, ele recebe o tamanho total da grade e roda um
# 	loop que itera enquanto a quantidade de bytes recebida for menor que
#	o tamanho total da grade
#
# 	Depois, o worker transforma os bytes em uma grade também, usand o mes-
#	mo módulo pickle. Após, ele pode fazer sua computacao normalmente. 



# módulo para comunicação com outros nós da rede
import socket

# módulo para serialização de JSON
import json

# módulo para transformar objetos Python em dados binários 
import struct

# módulo para chamadas de sistema
import sys

# type hints
import typing

'''
Solicita a entrada do nó na rede

Retorna um socket que será usado 
para se comunicar com o nó mestre
na rede
''' 
def entrada_rede():
	# cria e prepara o nó que vai receber conexoes para computacao
	server_socket = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM, socket,IPPROTO_TCP)
	server_socket.bind(('localhost', 0))
	server_socket.listen()

	# montagem da mensagem de entrada na rede
	# adaptar para o Tiny Protocol

	return server_socket

def calcular_grade(data: dict[str, Any]):
	pass

if __name__ == '__main__':
	s = entrada_rede()

	while True:
		conn_s, addr = s.accept()

		# adaptar para o Tiny Protocol

	s.shutdown(socket.SHUT_RDWR)
	s.close()
