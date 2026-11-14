# módulo para comunicação com outros nós da rede
import socket

# módulo para serialização de JSON
import json

# módulo para transformar objetos Python em dados binários 
import struct

# módulo para chamadas de sistema
import sys

# type hints
from typing import Any, List

# tiny protocol
from TinyProtocol import Tiny

# adaptar para o Tiny Protocol
def req_tipo_um(data: tuple, node_update: list[list[int]]):
	if data[0] != 1 or data[2] != 8888:
		return None

	node_update_b = pickle.dumps(node_update)
	packet = Tiny.build(
		1, 1, 5555,
		0, 0, 0, 0,
		node_update_b
	)

	return packet

# adaptar para o Tiny Protocol
def req_tipo_dois(data: tuple, node_update: list[list[int]]):
	# mudanca de planos, o nó trabalhador agora que vai
	# mandar a porta dele na rede. Como ta todo mundo
	# rodando na mesma maquina, nao tem problema ele mesmo
	# escolher a propria porta.

	

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
	s.bind(('localhost', 5555))
	s.listen()

	# node_update[0] -> novos nós; node_update[1] -> nós que saíram
	node_update = [[],[]]

	while True:
		conn_s, src_addr = s.accept()

		# recebe os campos fixos do pacote
		data_b = b''
		while len(data_b) < 24:
			data_b += s.recv(24)

		data = Tiny.dismantle_fixed(data_b)

		resp = None
		match data[0]:
			case 1:
				resp = req_tipo_um(data, node_update)
			case 2:
				resp = req_tipo_dois(data, node_update)
			case 3:
				resp = req_tipo_tres(data, node_update)
			case 4:
				conn_s.shutdown(socket.SHUT_RDWR)
				conn_s.close()
				break

		if resp: conn_s.sendall(resp)

		conn_s.shutdown(socket.SHUT_RDWR)
		conn_s.close()

	print('Nó BROKER saindo da rede...')

	s.shutdown(socket.SHUT_RDWR)
	s.close()
