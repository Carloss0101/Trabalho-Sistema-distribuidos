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

# info base fakenews
fakenews_path = Path('..')
sys.path.append(str(fakenews_path))
import fakenews

# copia profunda de objetos python
from copy import deepcopy

# serialização de objetos python em dados binários brutos
import pickle

'''
Solicita a entrada do nó na rede

Retorna um socket que será usado 
para se comunicar com o nó mestre
na rede
''' 
def entrada_rede():
	'''
	'''

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
		print(f'WORKER ({porta}) - FALHA NA CONEXÃO AO BROKER', end='\n\n')
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
		print(f'WORKER ({porta}) - ATIVO', end='\n\n')
		return server_socket

	print(f'WORKER ({porta}) - FALHA AO ENTRAR NA REDE', end='\n\n')
	sys.exit(1)

def req_tipo_zero(
	tiny_pck:    tiny.Tiny, 
	base_grid:   list[list[int]], 
	source_port: int,
	limiar:      int):
	'''
	'''

	# tuple[0] -> grade calculada;
	# tuple[1] -> inteiro (0 ou 1) que sinaliza existencia de ESPALHADOR 
	new_grid, esp_existe = fakenews.proxima_geracao_contar_estados(
		tiny_pck, 
		base_grid,
		limiar
	)

	new_grid_b = pickle.dumps(new_grid)
	esp_existe_b = int.to_bytes(esp_existe)
	result_b = new_grid_b + esp_existe_b

	# O envio da grade junto com o valor que representa se espalhadores
	# ainda existem segue o mesmo padrao que o envio da grade + limiar
	# para calculo partindo do nó mestre para os nós trabalhadores. 
	return tiny.Tiny(
		tipo=tiny_pck.tipo, req_res=1, source_port=source_port,
		row_start=tiny_pck.row_start, 
		row_end=tiny_pck.row_end,
		column_start=tiny_pck.column_start, 
		column_end=tiny_pck.column_end,
		data_length=len(new_grid_b),
		data=result_b
	).to_bytes()

def req_tipo_quatro(tiny_pck: tiny.Tiny, source_port: int):
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
		tipo=tiny_pck.tipo, req_res=1, source_port=source_port
	).to_bytes()

# acho que essa funcao é pra caso eu saia abruptamente da rede
# com CTRL + C. Ai tipo, eu criaria uma thread que chama essa
# funcao e dentro dessa funcao eu ficaria esperando por um
# input que seja CTRL + C. Caso esse input venha, eu apenas
# inicio uma comunicacao rapida com o no broker pra enviar
# uma mensagem do tipo 3 e sinalizar minha saida da rede
def cleanup():
	pass

if __name__ == '__main__':
	s = entrada_rede()

	conn_s, addr = s.accept()

	while True:

		tiny_pck_b = b''
		while len(tiny_pck_b) < 24:
			tiny_pck_b += conn_s.recv(24)

		tiny_pck = tiny.Tiny.ffields_to_tinyobj(tiny_pck_b)

		resp = None
		match tiny_pck.tipo:
			case 0:
				while len(tiny_pck.data) < tiny_pck.data_length:
					tiny_pck.data += conn_s.recv(tiny_pck.data_length)
				grid = tiny_pck.data_from_bytes()
				
				# tenho que lembrar de enviar o limiar concatenado logo
				# após a grade no pacote enviado pelo mestre. Nesse caso,
				# o bagulho é serializar a grade com pickle.dumps() e depois
				# serializar o limiar com int.to_bytes(), concatenar as duas
				# strings de bytes e enfiar no campo Data do pacote.
				# É meio gambiarra, mas fodasse
				limiar_b = b''
				while len(limiar_b) < 1:
					limiar_b += conn_s.recv(1)
				
				resp = req_tipo_zero(
					tiny_pck, 
					grid, 
					s.getsockname()[1], 
					int.from_bytes(limiar_b)
				)
			case 4:
				resp = req_tipo_quatro(tiny_pck, s.getsockname()[1])

		if resp: conn_s.sendall(resp)

		if tiny_pck.tipo==4: break

	print(f'WORKER ({s.getsockname()[1]}) SAINDO DA REDE...', end='\n\n')

	conn_s.shutdown(socket.SHUT_RDWR)
	conn_s.close()

	s.shutdown(socket.SHUT_RDWR)
	s.close()

