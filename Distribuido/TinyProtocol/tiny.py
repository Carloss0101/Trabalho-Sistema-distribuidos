# Implementação do Tiny Protocol. O protocolo foi criado com o único intuito
# de facilitar a comunição dos nós da rede distribuída.

#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|R|E|     |       |             |                               | 
#	|e|s|     |       |             |                               |
#	|q|p|     |       |             |                               |
#	|R|E|Tipo |Limiar |   Padding   |          Source Port          |
#	|e|x|     |       |             |                               |
#	|s|s|     |       |             |                               |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                   		Row Start                           |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           Column Start                        |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           Row End                             |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           Column End                          |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           R Row Start                         |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           R Column Start                      |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           R Row End                           |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           R Column End                        |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           Data Length                         |
#	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#	|                           Data                                
#	+-+-+-+-+-+-+-+-+-+-+-+.............

#	ReqRes: Indica se a mensagem é uma requisiçao ou uma resposta
#			
#			0 -> Requisição
#			1 -> Resposta
#
#	EspExs: Indica se pelo menos um espalhador existe no resultado
#			da computação realizada pelo worker. Enviado apenas na
#			troca de mensagens do tipo 0 entre o master e o worker.
#
#			0 -> Espalhador não existe na parte calculada
#			1 -> Espalhador existe na parte calculada
#
#	Tipo: Indica o tipo da mensagem. Pode ter qualquer valor de 0 a 4:
#		
#			0 -> Envio da grade para computação
#			1 -> Atualização dos nós ativos na rede
#			2 -> Entrada de um worker na rede
#			3 -> Saída de um worker da rede
#			4 -> Sinaliza fim da computacão
#
#	Limiar: Limiar de convencimento utilizado no cálculo do algoritmo.
#			Enviado apenas na troca de mensagens do tipo 0 entre o mas-
#			ter e o worker.
#
#			Valor -> 1 a 8
#
#	Padding: 7 bits 0 que servem apenas para preencher o pacote
#
#	Source Port: Porta do remetente. Essa porta é a porta que identifica o
#				 nó na rede
#
#	Row Start: Indica o índice inicial da linha na grade base que gerou
#			   a parte enviada para o nó worker. Ao juntar Row Start, 
#			   Column Start, Row End e Column End, é possível obter a 
#			   quantidade exata de células que o nó trabalhador terá
#			   que calcular
#
#	Row End: Indica o índice final da linha na grade base que gerou
#			 a parte enviada para o nó worker. Ao juntar Row Start, 
#			 Column Start, Row End e Column End, é possível obter a 
#			 quantidade exata de células que o nó trabalhador terá
#			 que calcular
#
#	Column Start: Indica o indice inicial da coluna na grade base que 
#				  gerou a parte enviada para o nó worker. Ao juntar 
#				  Row Start, Column Start, Row End e Column End, é pos-
#				  sível obter a quantidade exata de células que o nó 
#				  trabalhador terá que calcular
#
#	Column End: Indica o índice final da coluna na grade base que gerou a 
#				parte enviada para o nó worker. Ao juntar Row Start, 
#			    Column Start, Row End e Column End, é possível obter a 
#			    quantidade exata de células que o nó trabalhador terá
#			    que calcular
#
#	R Row Start: Indica o índice inicial da linha que gerou a parte enviada
#				 para o nó worker, porém ele inclui a linha adicional que é
#				 usada para calcular os vizinhos das células que ficam nas
#				 bordas da parte da grade. Quando o valor for igual a 
#				 (Row Start) - 1, existe uma linha adicional acima da primei-
#				 ra linha da parte enviada ao nó worker. Quando o valor for
#				 igual a Row Start, quer dizer que não existe uma linha adi-
#				 cional acima da primeira linha da parte enviada ao nó wor-
#				 ker, então a parte está na borda superior da grade original.
#
#	R Column Start: Indica o indice inicial da coluna que gerou a parte en-
#					viada para o nó worker, porém ele inclui a coluna adicio-
#					nal que é usada para calcular os vizinhos das células que
#					ficam nas bordas da parte da grade. Quando o valor for i-
#					gual a (Column Start) - 1, existe uma coluna adicional à
#					esquerda da primeira coluna da parte enviada ao nó worker.
#					Quando o valor for igual a Column Start, quer dizer que 
#					não existe uma coluna adicional à esquerda da primeira co-
#					luna na parte enviada ao nó worker, então a parte está na
#					borda esquerda da grade original.
#
#	R Row End: Indica o indice final da linha que gerou a parte enviada para o
#			   nó worker, porém ele inclui a linha adicional que é usada para
#			   calcular os vizinhos das células que ficam nas bordas da parte
#			   da grade. Quando o valor for igual a (Row End) + 1, existe uma
#			   linha adicional abaixo da última linha da parte enviada ao nó
#			   worker. Quando o valor for igual a Row end, quer dizer que não
#			   existe uma linha adicional abaixo da última linha na parte en-
#			   viada ao nó worker, então a parte está na borda inferior da
#			   grade original.
#
#	R Column End: Indica o indice final da coluna que gerou a parte enviada
#				  para o nó worker, porém ele inclui a coluna adicional que
#				  é usada para calcular os vizinhos das células que ficam nas
#				  bordas da parte da grade. Quando o valor for igual a 
#				  (Column End) + 1, existe uma coluna adicional à direita da
#				  última coluna da parte enviada ao nó worker. Quando o valor
#				  for igual a Column End, quer dizer que não existe uma coluna
#				  adicional à direita da última coluna na parte enviada ao nó
#				  worker, então a parte está na borda direita da 
#				  grade original.
#
#	Data Length: Indica o tamanho em bytes da parte da grade enviada. Na requi-
#				 sicão, será a parte da grade gerada a partir do resultado da
#				 geração anterior. Na resposta, será a parte da grade com os
#				 valores atualizados. Lembrando que na resposta a grade envi-
#				 ada não vai conter os vizinhos adicionais usados no cálculo,
#				 ja que eles não são mais necessários.
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
		req_res:      int,
		tipo:         int,
		source_port:  int,
		esp_ex:       int   = 0,
		limiar:       int   = 0, # depois disso tem um padding de 7 bits 0
		row_start:    int   = 0,
		col_start:    int   = 0,
		row_end:      int   = 0,
		col_end:      int   = 0,
		rrow_start:   int   = 0,
		rcol_start:   int   = 0,
		rrow_end:     int   = 0,
		rcol_end:     int   = 0,
		data_length:  int   = 0,
		data:         bytes = b''):
		'''
		Parameters
		----------
		req_res: int
			indica requisição ou resposta
		esp_ex: int, optional
			indica a existência de espalhadores. Deve ser 0 em qualquer
			troca de mensagens que não seja do tipo 0
		tipo: int
			tipo da mensagem
		limiar: int, optional
			limiar de convencimento. Deve ser 0 em qualquer troca de
			mensagens que não seja do tipo 0
		source_port: int
			porta identificadora na rede do nó que enviou o pacote
		row_start: int, optional
			indice de linha inicial que deu origem à parte da grade. Deve ser 
			0 em qualquer troca de mensagens que não seja do tipo 0
		col_start: int, optional
			indice de coluna inicial que deu origem à parte da grade. Deve
			ser 0 em qualque troca de mensagens que não seja do tipo 0
		row_end: int, optional
			indice de linha final que deu origem à parte da grade. Deve
			ser 0 em qualquer troca de mensagens que não seja do tipo 0
		col_end: int, optional
			indice de coluna final que deu origem à parte da grade. Deve
			ser 0 em qualquer troca de mensagens que não seja do tipo 0
		rrow_start: int, optional
			indice de linha inicial que deu origem à parte da grade. Já 
			expliquei a diferenca desse pro row_start. Deve ser 0 em qualquer
			troca de mensagens que não seja do tipo 0
		rcol_start: int, optional
			indice de coluna inicial que deu origem à parte da grade. Já 
			expliquei a diferença desse pro col_start. Deve ser 0 em qualquer
			troca de mensagens que não seja do tipo 0
		rrow_end: int, optional
			indice de linha final que deu origem à parte da grade. Já expliquei
			a diferença desse pro row_end. Deve ser 0 em qualquer troca de 
			mensagens que não seja do tipo 0
		rcol_end: int, optional
			indice de coluna final que deu origem à parte da grade. Já expli-
			quei a diferença desse pro col_end. Deve ser 0 em qualquer troca
			de mensagens que não seja do tipo 0
		data_length: int, optional
			tamanho em bytes da parte da grade enviada. Deve ser 0 em qualquer
			troca de mensagens que não seja do tipo 0
		data: bytes
			parte da grade enviada. Deve ser b'' em qualquer troca de mensa-
			gens que não seja do tipo 0
		'''

		self.req_res      = req_res
		self.esp_ex       = esp_ex
		self.tipo         = tipo
		self.limiar       = limiar
		self.source_port  = source_port
		self.row_start    = row_start
		self.col_start    = col_start
		self.row_end      = row_end
		self.col_end      = col_end
		self.rrow_start   = rrow_start
		self.rcol_start   = rcol_start
		self.rrow_end     = rrow_end
		self.rcol_end     = rcol_end
		self.data_length  = data_length if data_length else len(data)
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

		# valor que juntará os 5 primeiros campos
		# (req_res, esp_ex, tipo, limiar e padding)
		init_2_byte = 0

		# adiciona o valor de req_res
		init_2_byte ^= self.req_res

		# left shit 1 bit e adiciona o valor de esp_ex
		init_2_byte <<= 1
		init_2_byte ^= self.esp_ex

		# left shit 3 bits e adiciona o valor de tipo
		init_2_byte <<= 3
		init_2_byte ^= self.tipo

		# left shift 4 bits e adiciona o valor de limiar
		init_2_byte <<= 4
		init_2_byte ^= self.limiar

		# left shift de 7 bits para o padding
		init_2_byte <<= 7

		tiny_packet = struct.pack(
			'!HHIIIIIIIII',
			init_2_byte, self.source_port,
			self.row_start,
			self.col_start,
			self.row_end,
			self.col_end,
			self.rrow_start,
			self.rcol_start,
			self.rrow_end,
			self.rcol_end,
			self.data_length
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
			'!HHIIIIIIIII',
			 packet
		)

		# extrai os 2 primeiros bytes pra separar os campos
		init_2_byte = data[0]

		# retira o padding
		init_2_byte >>= 7

		# extrai o limiar
		limiar = init_2_byte & 0xF
		init_2_byte >>= 4

		# extrai o tipo
		tipo = init_2_byte & 0x7
		init_2_byte >>= 3

		# extrai o esp_ex
		esp_ex = init_2_byte & 0x1
		init_2_byte >>= 1

		# extrai o req_res
		req_res = init_2_byte & 0x1

		return Tiny(
			req_res=req_res, esp_ex=esp_ex, tipo=tipo, 
			limiar=limiar, source_port=data[1],
			row_start=data[2],
			col_start=data[3],
			row_end=data[4],
			col_end=data[5],
			rrow_start=data[6],
			rcol_start=data[7],
			rrow_end=data[8],
			rcol_end=data[9],
			data_length=data[10]
		)