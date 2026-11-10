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
#			 deverá ser computada. É inclusivo
#
#	Column Start: Indica o indice inicial da coluna que dará origem à grade
#				  que deverá ser computada. É inclusivo
#
#	Column End: Indica o índice final da coluna que dará origem à grade 
#				que deverá ser computada. É inclusivo			
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
	
	O protocolo TinyGrid foi desenvolvido com o intuito de facilitar a comu-
	nicão entre nós numa rede distribuída. O nome do protocolo vem da tarefa
	principal executada pelos nós da rede: Manipular uma grade (2D List).

	Methods
	-------
	to_bytes(self)
		Retorna o Tiny Packet em formato binário bruto

	data_from_bytes(self)
		Usado quando o campo Data Length do pacote é diferente de 0, trans-
		forma os dados binários presentes no campo Data em uma matriz que
		pode representar uma das três opcões:
			- Grade que serve como base para cálculo da grade da próxima
			  geracão do algoritmo. (Enviada pelo nó mestre aos workers)
			
			- Parte da grade da nova geracão calculada por um dos nós tra-
			  balhadores. (Enviada pelo worker ao nó mestre)

			- Uma lista 2D que contém as listas de novos nós da rede e nós
			  que saíram da rede. (Enviada pelo broker ao nó mestre)

	has_data(self)
		Verifica se o pacote tem uma grade presente no campo Data que deve
		ser recebida

	ffields_to_tinyobj(packet: bytes)
		Transforma os campos fixos do Tiny Packet em um objeto do tipo
		Tiny, contendo todos os campos fixos do pacote. O campo Data não
		é preenchido porque não é confirmado que haverá uma grade presente
		em todo os pacotes
	"""

	def __init__(self,
		tipo:         int,
		req_res:      int,
		source_port:  int,
		data_length:  int   = 0,
		row_start:    int   = 0,
		row_end:      int   = 0,
		column_start: int   = 0,
		column_end:   int   = 0,
		data:         bytes = b''):
		'''
		Parameters
		----------
		tipo : int
			Tipo da mensagem. Pode ter valores de 0 a 4
		req_res : int
			Indica Requisição (0) ou Resposta (1)
		source_port : int
			Porta que representa o nó que está enviando
			o pacote
		data_length : int, optional
			Tamanho em bytes da grade sendo enviada no pacote
		row_start : int, optional
			Indice inicial da linha da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem 
			que o tipo não é 0
		row_end : int, optional
			Indice final da linha da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem 
			que o tipo não é 0
		column_start : int, optional
			Indice inicial da coluna da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem 
			que o tipo não é 0
		column_end : int, optional
			Indice final da coluna da grade que o nó worker é responsável por
			calcular para a próxima geracão. Deve ser 0 em qualquer mensagem 
			que o tipo não é 0
		data : bytes, optional
			Grade a ser enviada no pacote em formato binário.
		'''

		self.tipo         = tipo
		self.req_res      = req_res
		self.source_port  = source_port
		self.data_length  = data_length if data_length else len(data)
		self.row_start    = row_start
		self.row_end      = row_end
		self.column_start = column_start
		self.column_end   = column_end
		self.data         = data

	def to_bytes(self):
		'''
		Constrói o Tiny Packet e o retorna em formato binário
		
		Returns
		-------
		tiny_packet : bytes
			Pacote em formato binário que representa um pacote do protocolo
			TinyGrid. Pode ou não conter uma grade no campo Data
		'''

		tiny_packet = struct.pack(
			'!BBHIIIII',
			self.tipo, self.req_res, self.source_port,
			self.data_length,
			self.row_start,    
			self.row_end,
			self.column_start, 
			self.column_end
		)

		if self.data: tiny_packet += self.data

		return tiny_packet

	def data_from_bytes(self):
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

		Returns
		-------
		pickle.loads(self.data): list[list[int]]
			Lista 2D que representa a grade enviada no campo Data do Tiny
			Packet
		'''

		return pickle.loads(self.data)

	def has_data(self):
		'''
		Determina se o pacote contém uma grade a ser recebida. Retorna 
		True caso o atributo data_length seja diferente de 0, False 
		caso contrário

		Returns
		-------
		self.data_length != 0: bool
			True caso tenha uma grade a ser recebida no pacote,
			False caso contrário
		'''

		return self.data_length != 0

	def ffields_to_tinyobj(packet: bytes):
		'''
		Fixed Fields to Tiny Object

		Traduz os dados binários que representam os campos fixos do Tiny Packet
		e retorna um objeto do tipo Tiny que representa o pacote.

		Esse método extrai apenas os campos fixos porque não é obrigatório que 
		todo Tiny Packet tenha uma grade no campo Data. Além disso, quando pre-
		sente, a grade pode variar de tamanho a cada chamada. Assim, o fluxo de
		operacões do nó que recebe um Tiny Packet deve ser:

						Depois de receber os 24 bytes que representam
						os campos fixos do pacote, ele chama o método
						ffields_to_tinyobj(packet)

											|
											v

						Ao chamar o método de instância has_data(), 
						caso o valor retornado seja True, o campo
						Data Length é != 0. Isso significa que uma
						grade está presente, então é necessário re-
						ceber o resto dos bytes enviados. A quanti-
						dade total de bytes recebidos é igual ao va-
						lor presente em Data Length

											|
											v

						Com os bytes armazenados, ele deve chamar o 
						método data_from_bytes() para obter a grade
						representada pelos bytes recebidos

		Parameters
		----------
		packet : bytes
			Os dados binários brutos que representam os campos fixos do 
			Tiny Packet

		Returns
		-------
		Tiny(...) : Tiny
			Objeto do tipo Tiny que representa um Tiny Packet
		'''
		
		data = struct.unpack(
			'!BBHIIIII',
			 packet
		)

		return Tiny(
			tipo=data[0], req_res=data[1], source_port=data[2],
			data_length=data[3],
			row_start=data[4],
			row_end=data[5],
			column_start=data[6],
			column_end=data[7])


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
	ROWEND_req = 2
	COLUMNSTART_req = 0
	COLUMNEND_req = 2

	tiny_pck = Tiny(
		tipo=TIPO_req,
		req_res=REQRES_req,
		source_port=SOURCEPORT_req,
		row_start=ROWSTART_req,
		row_end=ROWEND_req,
		column_start=COLUMNSTART_req,
		column_end=COLUMNEND_req,
		data=GRID_req
	)

	tiny_pck_b = tiny_pck.to_bytes()
	#########################################################

	# aqui seria o envio dos bytes por meio de sockets

	# FLUXO DE DESEMPACOTAMENTO DO PACOTE CONTENDO A GRADE
	#########################################################
	# Os campos fixos tem um tamanho total de 24 bytes
	fixed_fields_b = tiny_pck_b[:24]
	tiny_pck = Tiny.ffields_to_tinyobj(fixed_fields_b)
	print(tiny_pck.tipo, tiny_pck.req_res, tiny_pck.source_port)
	print(tiny_pck.data_length)
	print(tiny_pck.row_start)
	print(tiny_pck.row_end)
	print(tiny_pck.column_start)
	print(tiny_pck.column_end, end='\n\n')

	# converte a grade separadamente, como foi dito
	tiny_pck.data = tiny_pck_b[24:]
	if tiny_pck.has_data():
		grid = tiny_pck.data_from_bytes()
	print(grid)
	#########################################################
