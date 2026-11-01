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

	'''
	Constroi o Tiny packet
	Retorna a representacao binaria do pacote
	'''
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

	'''
	Transforma a representacao binaria do Tiny packet
	em uma tupla contendo todos os campos fixos do
	pacote. 

	Como assim todos os campos fixos ?

		Como o campo de Data do pacote pode variar de
		tamanho, ele nunca é lido antes dos campos
		fixos serem lidos e serializados. Então o que
		vai acontecer é:

			O nó vai receber os dados binários do 
			pacote por meio do socket

			Vai mandar os dados binários lidos para
			a funcao dismantle_fixed

			A funcao vai transformar os campos fixos
			em uma tupla e retorná-los ao chamador.

			Caso o campo Grid Size seja diferente de
			zero, o nó vai receber o resto dos dados
			binários e depois chamar a funcao dismantle_
			data para converter a grade para um objeto
			Python, já que esta vai estar em bytes.

	retorna a tupla contendo os campos fixos do pacote
	'''	
	def dismantle_fixed(packet: bytes):
		return struct.unpack(
			'!BBHIIIII',
			 packet
		)

	'''
	Transforma dados binarios em uma grade

	Na requisicao, o nó que destinatário vai usar
	essa funcão pra obter a grade que será base 
	para computacão da nova grade

	Ao receber a respota, o nó mestre vai usar essa 
	funcão para converter o formato binário da grade
	calculada para um objeto python

	Retorna a grade como uma matriz python (lista 2d)
	'''
	def dismantle_data(data: bytes):
		return pickle.loads(data)


import socket

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
