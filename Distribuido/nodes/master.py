# módulo para chamadas de sistema
import sys

# criacao de caminhos dinamicos para importacao
from pathlib import Path

sys.path.append(str(Path('../TinyProtocol')))
sys.path.append(str(Path('..')))

# módulo para comunicação com outros nós da rede
import socket

# módulo para transformar objetos Python em dados binários 
import struct

# tiny protocol
import tiny

# info. base fakenews
import fakenews

# serialização de objetos python em dados binários brutos
import pickle

# multi-threading para concorrẽncia em operações I/O
from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime

class WorkerFailException(Exception):
	pass

def dividir_grade(
	base_grid:    list[list[int]],
	worker_count: int):
	'''
	Divide a grade em partes de acordo com
	a quantidade de workers ativos na rede

	Parameters
	----------
	base_grid : list[list[int]]
		Objeto Python da grade para obter suas dimensoes
	worker_count : int
		Quantidade de workers ativos na rede

	Returns
	-------
	divisao_celulas : list[int]
		Lista onde cada elemento representa a quantidade
		de células que cada nó worker da rede vai ter
		que calcular. len(divisao_celulas) == worker_count
	'''

	cel_count = len(grid) * len(grid[0])
	divisao_celulas = [
		int(cel_count/worker_count) for _ in range(worker_count)
	]
	if divisao_celulas:
		divisao_celulas[-1] += cel_count % worker_count

	return divisao_celulas

def handle_conn(
	base_grid:      list[list[int]],
	base_grid_b:    bytes,
	limiar_b:       bytes,
	cel_count:      int,
	posicao_linear: int,
	workers:        dict,
	worker:         int):
	'''
	Manda parte da grade para cálculo para algum
	nó da rede representado pelo parâmetro worker

	Parameters
	----------
	base_grid : list[list[int]]
		Grade base para computacão em estado de
		Objeto Python
	base_grid_b : bytes
		Grade base para computacão em estado de
		dados binários brutos
	limiar_b : bytes
		Limiar de convencimento do algoritmo em
		estado de dados binários brutos
	cel_count : int
		Quantidade de células que o nó vai ter
		que calcular
	posicao_linear : int
		Posicao linear da célula de onde a com-
		putacao vai iniciar (célula inicial)
	workers : dict
		Dicionário que contém os workers ativos
		na rede. Serve para pegar o socket do 
		nó representado pelo parâmetro worker
		e também para atualizar seu estado na rede
	worker : int
		Numero inteiro que representa o identifica-
		dor do nó na rede (porta)

	Returns
	-------
	esp_existe : bool
		Valor booleano que define se um espalhador
		existe na parte da grade calculada pelo 
		nó representado pelo parâmetro worker.
		Isso não define sozinho se o algoritmo
		vai parar. Para parar, todos os nós wor-
		kers devem retornar False em suas funcões
		de computacão

		OBS: O objeto Python da grade atualizada
		não é retornado porque como a referencia
		da grade é passada para a funcao, seus 
		valores sao atualizados aqui mesmo
	'''

	# aqui cuida caso o numero de nos seja maior
	# que o necessario. Ai tipo, caso algum no
	# acabe ficando sem celulas pra calcular, nao
	# precisa de todo o overhead de troca de infor-
	# macoes, só deixa ele quieto
	if not cel_count: return True

	col_count = len(base_grid[0])

	# calculo da posicao inicial da divisao de celulas
	row_start = int(posicao_linear / col_count)
	col_start = posicao_linear % col_count

	# calculo da posicao final da divisao de celulas
	row_end = int((posicao_linear+(cel_count-1)) / col_count)
	col_end = (posicao_linear+(cel_count-1)) % col_count

	# so lembrando que agora row_end e column_end sao
	# inclusivos no protocolo TinyGrid
	t0 = tiny.Tiny(
		tipo=0, req_res=0, source_port=8888,
		data_length=len(grid_b),
		row_start=row_start, row_end=row_end,
		column_start=col_start, column_end=col_end,
		data=grid_b + limiar_b
	)

	t0_b = t0.to_bytes()

	conn_s = workers[worker]['s']
	conn_s.sendall(t0_b)

	t0_ans_b = b''
	while len(t0_ans_b) < 24:
		try:
			t0_ans_b += conn_s.recv(24)
		except TimeoutError:
			raise WorkerFailException()

	t0_ans = tiny.Tiny.ffields_to_tinyobj(t0_ans_b)

	# recebe a nova grade calculada
	while len(t0_ans.data) < t0_ans.data_length:
		try:
			t0_ans.data += conn_s.recv(t0_ans.data_length)
		except TimeoutError:
			# caso esteja unhealthy em duas rodadas
			# seguidas, remove o nó da rede
			raise WorkerFailException()

	grid_ans = t0_ans.data_from_bytes()

	# agora recebe a flag que sinaliza existencia de espalhadores
	esp_existe_b = b''
	while len(esp_existe_b) < 1:
		try:
			esp_existe_b += conn_s.recv(1)
		except TimeoutError:
			# caso esteja unhealthy em duas rodadas
			# seguidas, remove o nó da rede
			raise WorkerFailException()

	# confirma que o nó está ativo na rede
	workers[worker]['h'] = True

	esp_existe = int.from_bytes(esp_existe_b)

	# atualiza a grade base com os valores novos
	i,j = row_start, col_start
	while cel_count:
		base_grid[i][j] = grid_ans[i][j]
		if j+1 >= len(base_grid[i]):
			j = 0
			i += 1
		else:
			j += 1
		cel_count -= 1

	# retorna se existem espalhadores na parte da tabela
	# calculada pelo nó worker atual
	return bool(esp_existe)


def setup_master_node():
	'''
	Faz o setup inicial do nó mestre na rede distribuída

	Returns
	-------
	workers : dict
		Dicionário que armazena os nós da rede
		
		 VOU TER QUE MUDAR ESSA DESCRIÇÃO PORQUE AGORA TEM
		 APENAS OS NÓS DA REDE COMO UM TODO E SEU ESTADO É
		 REPRESENTADO UNICAMENTE PELA VARIAVEL 'h'.
		O dicionário contém duas chaves diferentes: 'ativos' e 
		'suspensos'.  A chave 'ativos' representa os nós que a-
		cabaram de entrar na rede e/ou os devolveram sua parte na 
		última geração do algoritmo. Nós que ficam duas rodadas 
		suspensos são removidos da rede.  
		Cada chave representa outro dicionário onde cada chave é
		um inteiro e seu valor é a porta do respectivo nó worker
		na rede. Por último, cada porta representa outro dicionário
		que tem os seguintes elementos: o socket usado para troca 
		de informações com o mesmo e um valor booleano que indica 
		se o nó está "healthy", ou seja, ele interagiu com o nó 
		mestre na ultima iteração do algoritmo ou acabou de entrar 
		na rede, quando o nó não responde a uma requisição de cál-
		culo do nó mestre, esse valor 'h' vira False. Ao ficar duas
		rodadas seguidas com esse valor setado em False, o nó é remo-
		vido da rede. Uma representação visual:

			workers: {
				1234: {
					's': obj Socket,
					'h': bool
				},

				5678: {
					's': obj Socket,
					'h': bool
				}
			}
	'''

	return {}

def update_worker_list(workers, cel_count: int):
	'''
	'''

	b_s = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

	code = b_s.connect_ex(('localhost', 5555))
	if code != 0:
		print('MASTER (8888) NÃO SE CONECTOU AO BROKER (5555)')
		sys.exit(1)

	t1 = tiny.Tiny(tipo=1, req_res=0, source_port=8888)
	t1_b = t1.to_bytes()

	b_s.sendall(t1_b)

	t1_ans_b = b''
	while len(t1_ans_b) < 24:
		t1_ans_b += b_s.recv(24)

	t1_ans = tiny.Tiny.ffields_to_tinyobj(t1_ans_b)
	while len(t1_ans.data) < t1_ans.data_length:
		t1_ans.data += b_s.recv(t1_ans.data_length)

	update_list = t1_ans.data_from_bytes()

	b_s.close()

	# atualiza novos workers
	for new_worker in update_list[0]:
		# socket de comunicacao com o worker
		s = socket.socket(
			socket.AF_INET, 
			socket.SOCK_STREAM, 
			socket.IPPROTO_TCP
		)

		code = s.connect_ex(('localhost', new_worker))

		if code != 0:
			s.shutdown(socket.SHUT_RDWR)
			s.close()
			continue

		workers[new_worker] = {
			's': s,
			'h': True
		}

	# define o timeout dos sockets de acordo com a quantidade
	# workers na rede
	timeout = 0.0005 * (cel_count / len(workers.keys()))
	for worker in workers.values():
		worker['s'].settimeout(timeout)

	# atualiza workers removidos
	active_workers = workers.keys()
	for rem_worker in update_list[1]:
		if rem_worker in active_workers:
			del workers[rem_worker]

# aqui ta errado porque nao ta atualizando a grade original
# depois da computacao. Porém como eu vou implementar essa
# funcao de forma que ela apenas chame handle_conn(), pode
# deixar assim por enquanto
def backup_handle_conn(
	healthy_workers: list[int],
	args:            tuple):
	'''

	args = (
		grid, grid_b, int.to_bytes(limiar),
		divisao_celulas[i], curr_pl, workers, 
		worker
	)

	future = executor.submit(handle_conn,
		args[0], args[1], args[2], args[3],
		args[4], args[5], args[6]
	)

	'''

	if len(healthy_workers) == 0:
		raise WorkerFailException()

	ans = False
	for worker in healthy_workers:
		try:
			ans = handle_conn(
				args[0], args[1], args[2],
				args[3], args[4], args[5], args[6])
			return ans
		except WorkerFailException:
			args[5][args[6]]['h'] = False

	raise WorkerFailException()

def master_backup(args: tuple):
	col_count = len(args[0][0])

	# calculo da posicao inicial da divisao de celulas
	row_start = int(args[4] / col_count)
	col_start = args[4] % col_count

	# calculo da posicao final da divisao de celulas
	row_end = int((args[4]+(args[3]-1)) / col_count)
	col_end = (args[4]+(args[3]-1)) % col_count

	# so lembrando que agora row_end e column_end sao
	# inclusivos no protocolo TinyGrid
	t0 = tiny.Tiny(
		tipo=0, req_res=0, source_port=8888,
		data_length=len(grid_b),
		row_start=row_start, row_end=row_end,
		column_start=col_start, column_end=col_end,
		data=args[1] + args[2]
	)

	new_grid, esp_existe = fakenews.proxima_geracao_contar_estados(
		t0, args[0], int.from_bytes(args[2])
	)

	# atualiza a grade base com os valores novos
	i,j = row_start, col_start
	cel_count = args[3]
	while cel_count:
		args[0][i][j] = new_grid[i][j]
		if j+1 >= len(args[0][i]):
			j = 0
			i += 1
		else:
			j += 1
		cel_count -= 1

	return bool(esp_existe)

# o comando para rodar o script master.py recebe como argumento
# de linha de comando os seguintes parâmetros:
#
#	linhas : int 
#		quantidade de linhas da grade
#	colunas : int
#		quantidade de colunas da grade
#	geracoes : int
#		quantidade de geracoes do algoritmo
#	pct_inf : float
#		porcentagem de influenciadores
#	pct_esp : float
#		porcentagem de espalhadores
#	pct_res : float
#		porcentagem de resistentes
#	limiar : int
# 		limiar de convencimento das células
#	show_grid : int
#		opcao para imprimir ou nao a grade,
#		pode ser 0 (n imp) ou qlqr outro (imp)
if __name__ == '__main__':
	# setup do master node na rede
	workers = setup_master_node()

	if len(sys.argv) != 9:
		print('usage: python master.py <arg1>...<arg9>')
		sys.exit(1)

	count_lin = int  (sys.argv[1])
	count_col = int  (sys.argv[2])
	count_ger = int  (sys.argv[3])
	pct_inf   = float(sys.argv[4])
	pct_esp   = float(sys.argv[5])
	pct_res   = float(sys.argv[6])
	limiar    = int  (sys.argv[7])
	show_grid = bool (int(sys.argv[8]))

	grid = fakenews.criar_grade(
		count_lin, 
		count_col,
		pct_esp, 
		pct_inf, 
		pct_res
	)

	fakenews.saudacao_alg(
		grid, 
		pct_esp, 
		pct_inf,
		pct_res, 
		count_ger,
		limiar
	)

	start_time = datetime.now().timestamp()

	for ger in range(count_ger):
		print('------------------------')
		print(f'Geração {ger+1:03d}')
		print('------------------------', end='\n\n')

		grid_b = pickle.dumps(grid)

		# atualizacao da lista de nos ativos na rede
		update_worker_list(workers, count_lin*count_col)

		# nos ativos na rede
		active_workers = list(workers.keys())
		len_active_workers = len(active_workers)

		# divide a grade de acordo com a quantidade de workers
		divisao_celulas = dividir_grade(grid, len_active_workers)

		futures = {}
		healthy_workers = []
		curr_pl = 0

		# variavel que define se existe pelo menos UM
		# espalhador na rede ainda
		next_ger = False

		# Pool de threads pra lidar com workers
		with ThreadPoolExecutor(max_workers=len_active_workers) as executor:
			for i, worker in enumerate(active_workers):
				args = (
					grid, grid_b, int.to_bytes(limiar),
					divisao_celulas[i], curr_pl, workers, 
					worker
				)

				future = executor.submit(handle_conn,
					args[0], args[1], args[2], args[3],
					args[4], args[5], args[6]
				)

				futures[future] = args

				curr_pl += divisao_celulas[i]

			# extrai o resultado das computacoes
			for future in as_completed(futures):
				try:
					args = futures[future]
					del futures[future]
					
					ans = future.result()

					if ans: next_ger = True

					healthy_workers.append(args[6])
				except WorkerFailException:
					# caso o nó esteja unhealthy a mais
					# de uma geração, o remove da rede
					if args[5][args[6]]['h'] == False:
						del args[5][args[6]]
					else:
						args[5][args[6]] = False

					future = executor.submit(
						backup_handle_conn, 
						healthy_workers, args
					)
					futures[future] = args

			master_node_calc = []

			# esse loop avalia os futures que fizeram
			# os calculos backup
			for future in as_completed(futures):
				try:
					args = futures[future]
					del futures[future]

					ans = future.result()

					if ans: next_ger = True
				
				except WorkerFailException:
					master_node_calc.append(args)

			# agora o nó mestre calcula as partes da grade
			# que sobraram
			for args in master_node_calc:
				# funcao que monta o pacote, manda pra
				# funcao do modulo fakenews.py e calcula
				ans = master_backup(args)

				if ans: next_ger = True

		if show_grid: fakenews.print_grid(grid)

		if not next_ger:
			print('\nO algoritmo terminou. Não há mais ESPALHADORES')
			break

	end_time = datetime.now().timestamp()

	exec_time = end_time - start_time

	print()
	print('=== RESULTADO FINAL ===')
	print('=======================')
	print(f'Tempo de execução: {exec_time:.4f}s')

	contagem_final = fakenews.contar_estados(grid)
	total_cel_count = count_lin * count_col

	fakenews.estatisticas_finais(total_cel_count, contagem_final)
