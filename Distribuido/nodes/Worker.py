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
import Tiny

'''
Solicita a entrada do nó na rede

Retorna um socket que será usado 
para se comunicar com o nó mestre
na rede
''' 
def entrada_rede():
	# criação do socket que vai representar o nó na rede
	server_socket = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
	server_socket.bind(('localhost', 0))
	server_socket.listen()

	# pacote de requisicao para entrada na rede
	porta = server_socket.getsockname()[1]
	packet = Tiny.Tiny.build(
		2, 0, porta,
		0, 0, 0, 0,
		None
	)

	# socket para envio do pacote de requisicao
	s = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
	code = s.connect_ex(('localhost', 5555))
	if code != 0:
		print('NÃO FOI POSSÍVEL SE CONECTAR AO BROKER (5555)')
		sys.exit(1)
	s.sendall(packet)

	# recebimento da resposta de entrada na rede
	data_b = b''
	while len(data_b) < 24:
		data_b += s.recv(24)

	s.shutdown(socket.SHUT_RDWR)
	s.close()

	# desserialização do pacote de resposta
	data = Tiny.Tiny.dismantle_fixed(data_b)
	if data[0]==2 and data[1]==1 and data[2]==5555:
		print(f'ENTRADA BEM SUCEDIDA - PORTA {porta}')
		return server_socket

	print(f'ERRO: NÓ {porta} NÃO CONSEGUIU ENTRAR NA REDE')
	sys.exit(1)

# requisicao do tipo 0, calculo da nova grade
def req_tipo_zero(data: tuple, base_grid: list[list[int]]):
	pass

if __name__ == '__main__':
	s = entrada_rede()

	while True:
		conn_s, addr = s.accept()

		data_b = b''
		while len(data_b) < 24:
			data_b += conn_s.recv(24)

		data = Tiny.Tiny.dismantle_fixed(data_b)

		resp = None
		match data[0]:
			case 0:
				grid_b = b''
				while len(grid_b) < data[3]:
					grid_b += conn_s.recv(data[3])
				grid = Tiny.Tiny.dismantle_data(grid_b)
				resp = req_tipo_zero(data, grid)
			case 4:
				conn_s.shutdown(socket.SHUT_RDWR)
				conn_s.close()
				break

		if resp: conn_s.sendall(resp)

		conn_s.shutdown(socket.SHUT_RDWR)
		conn_s.close()

	s.shutdown(socket.SHUT_RDWR)
	s.close()
