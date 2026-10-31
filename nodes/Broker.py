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

def req_tipo_um(data: dict[str, Any], novos: List:[int], saida: List[int]):
	if  data['tipo'] != 1 or data['src_port'] != 8888: 
		return None

	resp_b = json.dumps({
		'tipo': 1,
		'src_port': 5555,
		'novos': novos,
		'removidos': saida
	}).encode('UTF-8')

	novos.clear()
	saida.clear()

	return (struct.pack('!I', len(resp_b)), resp_b)

def req_tipo_dois(data: dict[str, Any], novos: List:[int]):
	# mudanca de planos, o nó trabalhador agora que vai
	# mandar a porta dele na rede. Como ta todo mundo
	# rodando na mesma maquina, nao tem problema ele mesmo
	# escolher a propria porta.

	if data['tipo'] == 2:
		novos.append(data['src_port'])

	return None

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
	s.bind(('localhost', 5555))
	s.listen()

	novos, saida = [],[]

	while True:
		conn_s, src_addr = s.accept()

		data_len_b = conn_s.recv(256)
		total_data_len = struct.unpack('!I', data_len_b)

		data_b = b''
		while len(data_b) < total_data_len:
			data_b += conn_s.recv(256)

		data = json.loads(data_b.decode('UTF-8'))

		resp = None
		match data['tipo']:
			case 1:  # update requisitado pelo no mestre
				resp = req_tipo_um(data, novos, saida)
			case 2:  # entrada de no worker na rede
				resp = req_tipo_dois(data, novos)
			case 3:  # saida de no worker da rede
				saida.append(src_addr[1])
			case 4:  # fim da computacao, sai da rede
				conn_s.close()
				break

		if resp: 
			conn_s.sendall(resp[0])
			conn_s.sendall(resp[1])
		
		conn_s.close()

	print('Nó BROKER saindo da rede...')

	s.close()
