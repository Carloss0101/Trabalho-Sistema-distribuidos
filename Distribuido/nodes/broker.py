# módulo para comunicação com outros nós da rede
import socket

# módulo para transformar objetos Python em dados binários 
import struct

# módulo para chamadas de sistema
import sys

# criacao de caminhos dinamicos para importacao
from pathlib import Path

# tiny protocol
tiny_path = Path('../TinyProtocol')
sys.path.append(str(tiny_path))
import tiny

# conversão de grade para bytes e bytes para grade
import pickle

def req_tipo_um(tiny_pck: tiny.Tiny, node_update: list[list[int]]):
	'''
	Trata mensagens do tipo 1. As mensagens do tipo 1 são enviadas
	pelo nó mestre para atualizar a tabela de nós ativos na rede

	Parameters
	----------
	data : tuple
		Tupla que contém os campos fixos do Tiny Packet
	node_update: list[list[int]]
		Lista bidimensional que representa a tabela de nós que 
		entraram e saíram da rede. O primeiro elemento é a lista
		de nós que entraram na rede, enquando o segundo elemento
		é a lista de nós que saíram da rede

	Returns
	-------
	packet : bytes
		Tiny Packet em formato binário bruto. Nesse pacote, o campo
		Data contém a tabela de atualização de nós ativos na rede
	'''

	node_update_b = pickle.dumps(node_update)
	packet = tiny.Tiny(
		tipo=tiny_pck.tipo, req_res=1, source_port=5555,
		data_length=len(node_update_b),
		data=node_update_b
	).to_bytes()

	node_update[0].clear()
	node_update[1].clear()

	return packet

def req_tipo_dois(tiny_pck: tiny.Tiny, node_update: list[list[int]]):
	'''
	Trata mensagem do tipo 2. As mensagens do tipo 2 são enviadas pelos
	nós trabalhadores para consolidar sua entrada na rede

	Parameters
	----------
	data : tuple
		Tupla que contém os campos fixos do Tiny Packet
	node_update : list[list[int]]
		Lista bidimensional que representa a tabela de nós que 
		entraram e saíram da rede. O primeiro elemento é a lista
		de nós que entraram na rede, enquando o segundo elemento
		é a lista de nós que saíram da rede

	Returns
	-------
	packet : bytes
		Tiny Packet em formato binário bruto. Nesse pacote, o campo
		Data Length vale 0 e o campo Data é vazio, porque não contém
		uma grade
	'''

	node_update[0].append(tiny_pck.source_port)

	packet = tiny.Tiny(
		tipo=tiny_pck.tipo, req_res=1, source_port=5555
	).to_bytes()

	# debug
	print('LISTA DE NÓS NOVOS ATUALIZADA')
	print(node_update[0])

	return packet

def req_tipo_tres(tiny_pck: tiny.Tiny, node_update: list[list[int]]):
	'''
	Trata mensagem do tipo 3. As mensagens do tipo 3 são enviadas pelos
	nós trabalhadores para consolidar sua saída da rede

	Parameters
	----------
	data : tuple
		Tupla que contém os campos fixos do Tiny Packet
	node_update : list[list[int]]
		Lista bidimensional que representa a tabela de nós que 
		entraram e saíram da rede. O primeiro elemento é a lista
		de nós que entraram na rede, enquando o segundo elemento
		é a lista de nós que saíram da rede

	Returns
	-------
	packet : bytes
		Tiny Packet em formato binário bruto. Nesse pacote, o campo
		Data Length vale 0 e o campo Data é vazio, porque não contém
		uma grade
	'''

	node_update[1].append(tiny_pck.source_port)

	packet = tiny.Tiny(
		tipo=tiny_pck.tipo, req_res=1, source_port=5555
	).to_bytes()

	# debug
	print('LISTA DE NÓS REMOVIDOS ATUALIZADA')
	print(node_update[1])

	return packet

def req_tipo_quatro(tiny_pck: tiny.Tiny):
	'''
	Trata mensagem do tipo 4. As mensagens do tipo 4 são enviadas pelo
	nó mestre para sinalizar o fim da execução do algoritmo

	Returns
	-------
	packet : bytes
		Tiny Packet em formato binário bruto. Nesse pacote, o campo
		Data Length vale 0 e o campo Data é vazio, porque não contém
		uma tabela
	'''

	return tiny.Tiny(
		tipo=tiny_pck.tipo, req_res=1, source_port=5555
	).to_bytes()

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
	s.bind(('localhost', 5555))
	s.listen()

	# node_update[0] -> novos nós
	# node_update[1] -> nós que saíram
	node_update = [[],[]]

	while True:
		conn_s, src_addr = s.accept()

		# recebe os campos fixos do pacote
		tiny_pck_b = b''
		while len(tiny_pck_b) < 24:
			tiny_pck_b += conn_s.recv(24)

		# converte os bytes dos campos fixos em um objeto Tiny
		tiny_pck = tiny.Tiny.ffields_to_tinyobj(tiny_pck_b)

		resp = None
		match tiny_pck.tipo:
			case 1:
				resp = req_tipo_um(tiny_pck, node_update)
			case 2:
				resp = req_tipo_dois(tiny_pck, node_update)
			case 3:
				resp = req_tipo_tres(tiny_pck, node_update)
			case 4:
				resp = req_tipo_quatro(tiny_pck)

		if resp: conn_s.sendall(resp)

		conn_s.shutdown(socket.SHUT_RDWR)
		conn_s.close()

		if tiny_pck.tipo==4: break

	print('BROKER (5555) saindo da rede...')

	s.shutdown(socket.SHUT_RDWR)
	s.close()
