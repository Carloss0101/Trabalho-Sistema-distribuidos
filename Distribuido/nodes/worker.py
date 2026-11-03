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
	packet = tiny.Tiny(
		tipo=2, req_res=0, source_port=porta
	).to_bytes()

	# socket para envio do pacote de requisicao
	s = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
	code = s.connect_ex(('localhost', 5555))
	if code != 0:
		print(f'ERRO: WORKER ({porta}) NÃO SE CONECTOU AO BROKER (5555)')
		sys.exit(1)
	s.sendall(packet)

	# recebimento da resposta de entrada na rede
	tiny_pck_b = b''
	while len(tiny_pck_b) < 24:
		tiny_pck_b += s.recv(24)

	s.shutdown(socket.SHUT_RDWR)
	s.close()

	# desserialização do pacote de resposta
	tiny_pck = tiny.Tiny.ffields_to_tinyobj(tiny_pck_b)
	if (tiny_pck.tipo==2 and tiny_pck.req_res==1 and
		tiny_pck.source_port==5555):
		print(f'ENTRADA BEM SUCEDIDA - WORKER ({porta})')
		return server_socket

	print(f'ERRO: WORKER ({porta}) NÃO CONSEGUIU ENTRAR NA REDE')
	sys.exit(1)

# requisicao do tipo 0, calculo da nova grade
def req_tipo_zero(tiny_pck: tiny.Tiny, base_grid: list[list[int]]):
	pass

if __name__ == '__main__':
	s = entrada_rede()

	while True:
		conn_s, addr = s.accept()

		tiny_pck_b = b''
		while len(tiny_pck_b) < 24:
			tiny_pck_b += conn_s.recv(24)

		tiny_pck = tiny.Tiny.ffields_to_tinyobj(tiny_pck_b)

		resp = None
		match data[0]:
			case 0:
				while len(tiny_pck.data) < tiny_pck.data_length:
					tiny_pck.data += conn_s.recv(tiny_pack.data_length)
				grid = tiny_pck.data_from_bytes()
				resp = req_tipo_zero(tiny_pck, grid)
			case 4:
				conn_s.shutdown(socket.SHUT_RDWR)
				conn_s.close()
				break

		if resp: conn_s.sendall(resp)

		conn_s.shutdown(socket.SHUT_RDWR)
		conn_s.close()

	s.shutdown(socket.SHUT_RDWR)
	s.close()
