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
	# tuple[1] -> dicionario de contagem de estados; 
	new_grid, count_st = fakenews.proxima_geracao_contar_estados(
		tiny_pck, 
		base_grid,
		limiar
	)

	count_st_b = pickle.dumps(count_st)
	new_grid_b = pickle.dumps(new_grid)
	result_b = count_st_b+new_grid_b

	# Pensei numa coisa pra resolver o problema de enviar apenas
	# o tamanho da grade no campo Data length:
	# Tipo assim, eu sempre vou mandar isso de volta pro nó mes-
	# tre, depois de ele ter enviado pro cálculo. Por esse fato,
	# e também pelo fato de que eu não altero o tamanho da grade
	# (o cálculo é feito sobre a grade enviada), o nó mestre já
	# tem o tamanho da grade enviada, então eu nao preciso man-
	# dar de volta

	# Dito isso, é possivel fazer o seguinte: 
	# Empacota os dois (new_grid e count_st) para dados binários
	# brutos, porém concatena com o dicionario count_st na frente,
	# e no campo Data Length coloca o tamanho dele, ao inves de
	# colocar o tamanho da grade, que o nó mestre ja tem. Na hora
	# de receber o pacote, o nó mestre lê o dicionario primeiro, 
	# antes da grade. Após ler o dicionario, basta ler o restan-
	# dos bytes que representam a grade.

	# No envio da grade junto com o limiar pelo nó mestre eu não
	# preciso fazer isso porque o limiar vai sempre variar de va-
	# lores entre 1 e 8 (inclusivo). A representação binária do
	# maior valor possível é 1000 (8), que ocupa 4 bits. Assim,
	# eu preciso ler no máximo 1 byte de dados na função recv()
	# do socket. Esse ja ta implementado, é só olhar na main
	# quando o match cai no case 0.
	return tiny.Tiny(
		tipo=tiny_pck.tipo, req_res=1, source_port=source_port,
		row_start=tiny_pck.row_start, 
		row_end=tiny_pck.row_end,
		column_start=tiny_pck.column_start, 
		column_end=tiny_pck.column_end,
		data_length=len(count_st_b),
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

if __name__ == '__main__':
	s = entrada_rede()

	while True:
		conn_s, addr = s.accept()

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

		conn_s.shutdown(socket.SHUT_RDWR)
		conn_s.close()

		if tiny_pck.tipo==4: break

	print(f'WORKER ({s.getsockname()[1]}) SAINDO DA REDE...', end='\n\n')

	s.shutdown(socket.SHUT_RDWR)
	s.close()

