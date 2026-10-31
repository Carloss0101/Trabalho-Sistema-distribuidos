# socket usado -> (AF_INET, SOCK_STREAM, IPPROTO_TCP)
# fluxo para serializar e desserializar a grade na hora do envio:
#
#	Servidor transforma a grade em bytes por meio do módulo "pickle"
# 
#	Servidor calcula o tamanho total em bytes da grade serializada. 
#	Isso seria feito armazenando a grade serializada em uma variável
#	e depois medindo o tamanho com len(var)
#
#	Após o cálculo e armazenamento do tamanho, o servidor usa o módu-
#	lo "struct" para transformar esse valor em bytes. Assim, o servidor
#	envia ao determinado nó o tamanho da grade que será enviada, antes
#	de enviar a grade em si.
#
#	Após o envio do tamanho da grade, o servidor envia a própria grade.


#	Do lado do nó worker, ele recebe o tamanho total da grade e roda um
# 	loop que itera enquanto a quantidade de bytes recebida for menor que
#	o tamanho total da grade
#
# 	Depois, o worker transforma os bytes em uma grade também, usand o mes-
#	mo módulo pickle. Após, ele pode fazer sua computacao normalmente. 



# módulo para comunicação com outros nós da rede
import socket

# módulo para serialização de JSON
import json

# módulo para transformar objetos Python em dados binários 
import struct

# módulo para chamadas de sistema
import sys

def entrada_rede():

if __name__ == '__main__':
	