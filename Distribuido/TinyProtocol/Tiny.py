# Implementação do Tiny Protocol. O protocolo foi criado com o único intuito
# de facilitar a comunição dos nós da rede distribuída.

#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	| Tipo - 8 bits |ReqRes - 8 bits|    Source Port - 16 bits      |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                        Data Length - 32 bits                  |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                        Row Start - 32 bits                    |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                        Row End - 32 bits                      |
# 	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                        Column Start - 32 bits                 |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                        Column End - 32 bits                   |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|					Data - Tamanho em bytes variavel
#	+-+-+-+-+-+-+-+-+-+-+-+.............
#
#
#	Tipo: Indica o tipo da mensagem. Pode ter qualquer valor de 0 a 4:
#		
#			0 -> Envio da grade para computação
#			1 -> Atualização dos nós ativos na rede
#			2 -> Entrada de um worker na rede
#			3 -> Saída de um worker da rede
#			4 -> Sinaliza fim da computacão
#
#	ReqRes: Indica se a mensagem é uma requisição ou resposta
#
#			0 -> Requisição
#			1 -> Resposta
#
#	Source Port: Porta do remetente. Essa porta é a porta que identifica o
#				 nó na rede
#
#	Data Length: Indica o tamanho em bytes da grade enviada. Na requisicão, 
#                será a grade gerada na computacão da geracão passada, que 
#                servirá como base para o cálculo da nova geracão. Na resposta 
#                será o resultado do cálculo da nova geracão
#
#	Row Start: Indica o índice inicial da linha que dará origem à grade
#			   que deverá ser computada. É inclusivo - 32 bits
#
#	Row End: Indica o índice final da linha que dará origem à grade que
#			 deverá ser computada. É exclusivo
#
#	Column Start: Indica o indice inicial da coluna que dará origem à grade
#				  que deverá ser computada. É inclusivo
#
#	Column End: Indica o índice final da coluna que dará origem à grade 
#				que deverá ser computada. É exclusivo			
#
#	Data: Os dados enviados no pacote. Na requisicão, será a grade base para
#		  computacão da grade da nova geracão. Na resposta, será a grade re-
#	      sultado da computacão da nova geracão.
#
#		  A grade já deve estar em formato BINÁRIO. Isso se deve ao fato de
#		  que seria extremamente ineficiente converter uma grade gigante para
#		  seu formato binário toda vez que o nó mestre fosse fazer seu envio
#		  para cada um dos nós da rede. Ao mandar seu formato binário para a 
#		  o pacote, ele precisa fazer essa conversão apenas uma vez.
#
#		  Para converter a grade para um formato binário, deve-se usar o méto-
#		  do dumps() do módulo padrão 'pickle'.

import struct, pickle

class Tiny:
	"""
	Classe que implementa o protocol TinyGrid
	
	########################################################################
	O protocolo TinyGrid foi desenvolvido com o intuito de facilitar a comu-
	nicão entre nós numa rede distribuída. O nome do protocolo vem da tarefa
	principal executada pelos nós da rede: Manipular uma grade (2D List).

	Methods
	-------
	build(tipo, req_req, source_port, row_start, row_end, column_start,
		  column_end, base_grid)
		Constrói o Tiny Packet e o retorna em formato binário

	dismantle_fixed(packet)
		Traduz os dados binários que representam os campos fixos do Tiny
		packet e retorna uma tupla de 8 elementos representando cada um,
		na ordem que são posicionados no pacote.

	dismantle_data(data)
		Usado quando o campo Data Length do pacote é diferente de 0, trans-
		forma os dados binários presentes no campo Data em uma matriz que
		pode representar uma das três opcões:
			- Grade que serve como base para cálculo da grade da próxima
			  geracão do algoritmo. (Enviada pelo nó mestre aos workers)
			
			- Parte da grade da nova geracão calculada por um dos nós tra-
			  balhadores. (Enviada pelo worker ao nó mestre)

			- Uma lista 2D que contém as listas de novos nós da rede e nós
			  que saíram da rede. (Enviada pelo broker ao nó mestre)
	"""

	def build(
			tipo:          int,
			req_res:       int,
			source_port:   int,
			row_start:     int,
			row_end:       int,
			column_start:  int,
			column_end:    int,
			base_grid:     bytes
		):
		'''
		Constrói o Tiny Packet e o retorna em formato binário

		Parameters
		----------
		tipo : int
			Tipo da mensagem. Varia de 0 a 4
		req_res : int
			Requisicão (0) ou Resposta (1)
		source_port : int
			Porta que representa o nó remetente na rede
		row_start : int 
			Indice inicial da linha da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem 
			que o tipo não é 0
		row_end : int
			Indice final da linha da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem
			que o tipo não é 0
		column_start : int
			Indice inicial da coluna da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem
			que o tipo não é 0
		column_end: int
			Indice final da coluna da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem
			que o tipo não é 0

		Returns
		-------
		tiny_packet : bytes
			Pacote em formato binário que representa um pacote do protocolo
			TinyGrid. Pode ou não conter uma grade no campo Data
		'''

		if base_grid:
			base_grid_size = len(base_grid)
		else:
			base_grid_size = 0

		tiny_packet = struct.pack(
			'!BBHIIIII',
			tipo, req_res, source_port,
			base_grid_size,
			row_start, row_end,
			column_start, column_end
		)

		if base_grid: tiny_packet += base_grid

		return tiny_packet
	
	def dismantle_fixed(packet: bytes):
		'''
		Traduz os dados binários que representam os campos fixos do Tiny Packet
		e retorna uma tupla de 8 elementos representando cada um, na ordem que 
		são posicionados no pacote.

		Esse método extrai apenas os campos fixos porque não é obrigatório que 
		todo Tiny Packet tenha uma grade no campo Data. Além disso, quando pre-
		sente, a grade pode variar de tamanho a cada chamada. Assim, o fluxo de
		operacões do nó que recebe um Tiny Packet deve ser:

						Depois de receber os 24 bytes que representam
						os campos fixos do pacote, ele chama o método
						dismantle_fixed(packet)

											|
											v

						Caso o campo Data Length seja diferente de 0, 
						uma grade está presente, então ele deve rece-
						ber o resto dos bytes enviados. A quantidade
						total de bytes recebidos é igual ao valor
						presente em Data Length

											|
											v

						Com os bytes armazenados, ele deve chamar o 
						método dismantle_data(data) para obter a gra-
						de representada pelos bytes recebidos

		Parameters
		----------
		packet : bytes
			Os dados binários brutos que representam os campos fixos do 
			Tiny Packet

		Returns
		-------
		struct.unpack(...) : tuple
			Tupla de 8 elementos, onde cada elemento representa um campo
			fixo do Tiny Packet e é algum Objeto Python
		'''
		return struct.unpack(
			'!BBHIIIII',
			 packet
		)

	def dismantle_data(data: bytes):
		'''
		Usado quando o campo Data Length do pacote é diferente de 0, trans-
		forma os dados binários presentes no campo Data em uma matriz que
		pode representar uma das três opcões:
			- Grade que serve como base para cálculo da grade da próxima
			  geracão do algoritmo. (Enviada pelo nó mestre aos workers)
			
			- Parte da grade da nova geracão calculada por um dos nós tra-
			  balhadores. (Enviada pelo worker ao nó mestre)

			- Uma lista 2D que contém as listas de novos nós da rede e nós
			  que saíram da rede. (Enviada pelo broker ao nó mestre)

		Parameters
		----------
		data : bytes
			Dados binários brutos que representam a grade enviada no campo
			Data do Tiny Packet

		Returns
		-------
		pickle.loads(data): list[list[int]]
			Lista 2D que representa a grade enviada no campo Data do Tiny
			Packet
		'''

		return pickle.loads(data)




	
# O CÓDIGO ABAIXO SERVE APENAS PARA TESTES
if __name__ == '__main__':

	# FLUXO DE MONTAGEM DO PACOTE DE ENVIO DA GRADE
	#########################################################
	GRID_req = pickle.dumps([
		[1,1,1],
		[1,1,1],
		[1,1,1]
	])
	TIPO_req = 0
	REQRES_req = 0
	SOURCEPORT_req = 5555
	ROWSTART_req = 0
	ROWEND_req = 3
	COLUMNSTART_req = 0
	COLUMNEND_req = 3

	packet = Tiny.build(
		tipo=TIPO_req,
		req_res=REQRES_req,
		source_port=SOURCEPORT_req,
		row_start=ROWSTART_req,
		row_end=ROWEND_req,
		column_start=COLUMNSTART_req,
		column_end=COLUMNEND_req,
		base_grid=GRID_req
	)
	#########################################################

	# FLUXO DE DESEMPACOTAMENTO DO PACOTE CONTENDO A GRADE
	#########################################################
	# Os campos fixos tem um tamanho total de 24 bytes
	fixed_fields_b = packet[:24]
	fixed_fields = Tiny.dismantle_fixed(fixed_fields_b)
	print(fixed_fields, end='\n\n')

	# converte a grade separadamente, como foi dito
	grid_b = packet[24:]
	grid = Tiny.dismantle_data(grid_b)
	print(grid)
	#########################################################
