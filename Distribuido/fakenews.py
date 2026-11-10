'''Base de utilitários do algoritmo Fake News

O Script contém quaisquer utilitários que sejam relacionados ao algoritmo em
si, como funções e variáveis. Isso foi feito com o intuito de separar as fun-
cionalidades exclusivas de cada nó (no contexto da rede distribuída) das fer-
ramentas necessárias para executar o algoritmo completo. 

Mesmo as funções modificadas, como a junção da contar_estados() com a função
proxima_geracao(), estão incluídas aqui. 
'''

import sys, random

from datetime import datetime

from copy import deepcopy

from pathlib import Path
sys.path.append(str(Path('./TinyProtocol')))
import tiny

IGNORANTE     = 0
ESPALHADOR    = 1
INATIVO       = 2
INFLUENCIADOR = 3
RESISTENTE    = 4

def contar_vizinhos(
	grid: list[list[int]],
	i:     int,
	j:     int):
	'''
	Conta a quantidade de cada tipo de vizinho da célula grid[i][j] uti-
	de acordo com a vizinhança de Moore

	A vizinhança de Moore é representada pelas 8 células vizinhas da cé-
	lula grid[i][j]. Em uma matriz 3x3, onde grid[i][j] é X e os vizinhos
	são O:

								O O O
								O X O
								O O O

	Parameters
	----------
	grid : list[list[int]]
		Grade utilizada na contagem
	i : int
		Posição de linha da célula
	j : int
		Posição de coluna da célula

	Returns
	-------
	vizinhos : dict[int, int]
		Dicionário que contém a contagem de 
		cada tipo de célula na grade 

	'''

	vizinhos = {
		IGNORANTE:     0,
		ESPALHADOR:    0,
		INATIVO:       0,
		INFLUENCIADOR: 0,
		RESISTENTE:    0
	}

	for di in [-1, 0, 1]:
		for dj in [-1, 0, 1]:
			if di == 0 == dj: continue

			ni = i + di
			nj = j + dj

			if (0 <= ni < len(grid) and
				0 <= nj < len(grid[0])):
				vizinhos[grid[ni][nj]] += 1

	return vizinhos

def contar_estados(grid: list[list[int]]):
	'''
	Conta e devolve os estados presentes na grade

	Essa funcão segue a implementacão padrão da funcão 
	contar_estados() presente no algoritmo sequencial
	e serve apenas para fazer a primeiro contagem de 
	estados no estágio de iniciacão do algoritmo

	Parameters
	----------
	grid : list[list[int]]
		Grade sobre a qual a contagem será realizada

	Returns
	-------
	estados_count: dict[int, int]
		Dicionário contendo a contagem de cada tipo de célula


	'''

	estados_count = {
		IGNORANTE:     0,
		ESPALHADOR:    0,
		INATIVO:       0,
		INFLUENCIADOR: 0,
		RESISTENTE:    0
	}

	for l in grid:
		for e in l:
			estados_count[e] += 1

	return estados_count

def proxima_geracao_contar_estados(
	tiny_pck:  tiny.Tiny,
	base_grid: list[list[int]],
	limiar:    int):
	'''
	Usada pelo nó worker para calcular sua parte da grade para a próxima
	geração. Essa função é uma junção das funções proxima_geracao() e 
	contar_estados(). O intuito da junção foi aproveitar a conexão do
	nó mestre ao nó trabalhador para envio da grade de cálculo, assim
	o nó trabalhador apenas conta cada tipo de célula na sua parte da
	grade e o nó mestre fica responsável apenas por juntar todos os
	resultados, evitando que outra conexão tenha que ser estabeleci-
	da apenas para contar estados (ou pior, que seria o nó mestre
	ter que contar todos os estados depois)

	Sobre o cálculo da quantidade de células presentes na parte da
	grade que está entre (row_start, column_start) - (row_end, col-
	umn_end):

		Dada uma coordenada qualquer a[i][j], para calcular sua po-
		sição linear numa matriz MxN (0-indexed):

			PL = i * N + j

		Agora, para saber a quantidade de elementos presentes entre 
		dois elementos quaisquer (inclusivo), calcule a PL dos dois
		elementos, PL1 e PL2.

			Quantidade de elementos = |PL1 - PL2| + 1

	Parameters
	----------
	tiny_pck : Tiny
		Tiny packet enviado na requisição pelo nó mestre
	base_grid : list[list[int]]
		Grade resultado da geração anterior. Serve de base para
		o cálculo da nova geração
	limiar : int
		Limiar de convencimento utilizado no algoritmo

	Returns
	-------
	(n_grid, espalhador_existe) : tuple
		Tupla que contém a grade com a parte atualizada e um valor
		inteiro que pode ser 1 ou 0, dependendo se a contagem de
		estados tem pelo menos um ESPALHADOR ou se todos acabaram
	'''

	i_start, i_end = tiny_pck.row_start,    tiny_pck.row_end
	j_start, j_end = tiny_pck.column_start, tiny_pck.column_end

	col_count = len(base_grid[0])
	cel_count = abs(
		(i_start * col_count + j_start) -
		(i_end   * col_count + j_end)
	) + 1

	n_grid = deepcopy(base_grid)
	estados_count = {
		IGNORANTE:     0,
		ESPALHADOR:    0,
		INATIVO:       0,
		INFLUENCIADOR: 0,
		RESISTENTE:    0
	}

	i,j = i_start, j_start
	while cel_count:
		vizinhos = contar_vizinhos(base_grid, i, j)

		if base_grid[i][j] == IGNORANTE:
			if (vizinhos[ESPALHADOR] >= limiar or
				vizinhos[INFLUENCIADOR] >= 1):
				n_grid[i][j] = ESPALHADOR

		elif base_grid[i][j] == ESPALHADOR:
			if (vizinhos[ESPALHADOR] >= limiar and
				vizinhos[INFLUENCIADOR] >= 1):
				n_grid[i][j] = INFLUENCIADOR
			else:
				n_grid[i][j] = INATIVO

		elif base_grid[i][j] == INFLUENCIADOR:
			if (not vizinhos[IGNORANTE]  and
				not vizinhos[ESPALHADOR] and
				not vizinhos[RESISTENTE]):
				n_grid[i][j] = INATIVO

		elif base_grid[i][j] == RESISTENTE:
			if (vizinhos[ESPALHADOR] >= limiar and
				vizinhos[INFLUENCIADOR] >= 1):
				n_grid[i][j] = ESPALHADOR

		estados_count[n_grid[i][j]] += 1

		if j+1 >= len(base_grid[i]):
			i += 1
			j = 0
		else:
			j += 1

		cel_count -= 1

	return (n_grid, 1 if estados_count[ESPALHADOR] != 0 else 0)

def criar_grade(
	count_lin: int,
	count_col: int,
	pct_esp:   float,
	pct_inf:   float,
	pct_res:   float):
	'''
	Cria a grade para execução do algoritmo

	Parameters
	----------
	count_lin : int
		Quantidade de linhas da grade
	count_col : int
		Quantidade de colunas da grade
	pct_esp : float
		Percentual de espalhadores na grade
	pct_inf : float
		Percentual de influenciadores na grade
	pct_res : float
		Percentual de resistentes na grade

	Returns
	-------
	grid : list[list[int]]
		Grade do algoritmo
	'''

	#random.seed(datetime.now().timestamp())
	random.seed(1)

	grid = [[IGNORANTE for _ in range(count_col)] for _ in range(count_lin)]

	for _ in range(int(count_lin*count_col*pct_esp)):
		i = random.randint(0, count_lin-1)
		j = random.randint(0, count_col-1)
		grid[i][j] = ESPALHADOR

	for _ in range(int(count_lin*count_col*pct_inf)):
		i = random.randint(0, count_lin-1)
		j = random.randint(0, count_col-1)
		grid[i][j] = INFLUENCIADOR

	for _ in range(int(count_lin*count_col*pct_res)):
		i = random.randint(0, count_lin-1)
		j = random.randint(0, count_col-1)
		grid[i][j] = RESISTENTE

	return grid

def print_grid(
	grid: list[list[int]],
	lim:  int = 30):
	'''
	Imprime a grade
	
	Parameters
	----------
	grid : list[list[int]]
		Grade a ser impressa
	lim : int, optional
		Limite de quantidade de linhas e colunas do total da grade que
		podem ser impressos
	'''

	simbolos = {
		IGNORANTE:     '.',
		ESPALHADOR:    'E',
		INATIVO:       'N',
		INFLUENCIADOR: 'I',
		RESISTENTE:    'R'
	}
	
	for i in range(min(len(grid), lim)):
		for j in range(min(len(grid[i]), lim)):
			print(simbolos[grid[i][j]], end=' ')
		print()
	print()

def saudacao_alg(
	grid:      list[list[int]],
	pct_esp:   float,
	pct_inf:   float,
	pct_res:   float,
	count_ger: int,
	limiar:    int):
	'''
	'''

	l, c = len(grid), len(grid[0])

	count_estados = contar_estados(grid)

	print("=== SIMULAÇÃO DISTRIBUÍDA DE PROPAGAÇÃO DE FAKE NEWS ===")
	print("========================================================")
	print(f'Grade: {l} x {c} - {l*c} Pessoas')
	print(f'Gerações: {count_ger}')
	print(f'Pct. inicial de espalhadores: {pct_esp*100:.2f}%',
		f'   - {count_estados[ESPALHADOR]} espalhadores reais')
	print(f'Pct. inicial de influenciadores: {pct_inf*100:.2f}%',
		f'- {count_estados[INFLUENCIADOR]} influenciadores reais')
	print(f'Pct. inicial de resistentes: {pct_res*100:.2f}%',
		f'   - {count_estados[RESISTENTE]} resistentes reais')
	print(f'Limiar de convencimento: {limiar} vizinhos')
	print("========================================================")
	print()

def estatisticas_finais(
    total: int,
    contagem_final:  dict[int. int]):
    '''
    '''

    print(f'Ignorantes finais: {contagem_final[IGNORANTE]:,}          \
    	 ({contagem_final[IGNORANTE] / total * 100:,.2f}%)')
    print(f'Espalhadores finais: {contagem_final[ESPALHADOR]:,}       \
    	 ({contagem_final[ESPALHADOR] / total * 100:,.2f}%)')
    print(f'Resistentes finais: {contagem_final[RESISTENTE]:,}        \
    	 ({contagem_final[RESISTENTE] / total * 100:,.2f}%)')
    print(f'Influenciadores finais: {contagem_final[INFLUENCIADOR]:,} \
    	 ({contagem_final[INFLUENCIADOR] / total * 100:,.2f}%)')
    print(f'Inativos finais: {contagem_final[INATIVO]:,}              \
    	 ({contagem_final[INATIVO] / total * 100:,.2f}%)')