import random
from multiprocessing import RawArray, Process, Barrier
from worker import worker
import time

IGNORANTE = 0
ESPALHADOR = 1
INATIVO = 2
INFLUENCIADOR = 3
RESISTENTE = 4

def criar_grade(linhas, colunas, seed, pct_espalhadores=0.02, pct_influenciadores=0.01, pct_resistentes=0.1):
    random.seed(seed)

    grade = [[IGNORANTE for _ in range(colunas)] for _ in range(linhas)]

    total_celulas         = linhas * colunas
    total_espalhadores    = int(total_celulas * pct_espalhadores)
    total_influenciadores = int(total_celulas * pct_influenciadores)
    total_resistentes     = int(total_celulas * pct_resistentes)

	# seta espalhadores na grade
    for _ in range(total_espalhadores):
        i = random.randint(0, linhas - 1)
        j = random.randint(0, colunas - 1)
        grade[i][j] = ESPALHADOR

    # seta influenciadores na grade
    for _ in range(total_influenciadores):
        i = random.randint(0, linhas - 1)
        j = random.randint(0, colunas - 1)
        grade[i][j] = INFLUENCIADOR

	# seta resistentes na grade
    for _ in range(total_resistentes):
        i = random.randint(0, linhas-1)
        j = random.randint(0, colunas-1)
        grade[i][j] = RESISTENTE

    return grade

#Converte a grade inicial para um vetor linear em memória compartilhada.
def copiar_para_buffer(grade, buf, colunas):
    for i in range(len(grade)):
        for j in range(colunas):
            buf[i * colunas + j] = grade[i][j]

# Dividir as linhas entre os workers
# Retorna uma lista de tuplas (linha_inicial, linha_final), uma por worker.
# Exemplo: dividir_linhas(10, 4) -> [(0, 3), (3, 6), (6, 8), (8, 10)]
def dividir_linhas(total_linhas, num_workers):
    linhas_por_worker = total_linhas // num_workers   #parte igual para todos
    linhas_sobrando   = total_linhas % num_workers    #o que nao dividiu exato

    faixas = []
    linha_inicial = 0

    for worker in range(num_workers):
        #Os primeiros 'linhas_sobrando' workers recebem 1 linha a mais
        if worker < linhas_sobrando:
            quantidade = linhas_por_worker + 1
        else:
            quantidade = linhas_por_worker

        linha_final = linha_inicial + quantidade
        faixas.append((linha_inicial, linha_final))

        linha_inicial = linha_final   #a próxima faixa começa onde esta terminou

    return faixas

def executar_paralelo(linhas=100, colunas=100, nw=4, seed=42,
                      pct_espalhadores=0.05, pct_influenciadores=0.01,
                      pct_resistentes=0.1, geracoes=50, limiar_convencimento=2):
    nw = min(nw, linhas)

    grade = criar_grade(linhas, colunas, seed=seed,
                        pct_espalhadores=pct_espalhadores,
                        pct_influenciadores=pct_influenciadores,
                        pct_resistentes=pct_resistentes)
    
    #Cria 2 buff, um com a grade atual e outro com a grade que será escrita pelos works, assim eles vao revisando
    #Sempre uma para leitura e outra para escrita..
    bufA = RawArray('b', linhas * colunas)
    bufB = RawArray('b', linhas * colunas)
    copiar_para_buffer(grade, bufA, colunas)

    faixas = dividir_linhas(linhas, nw)

    barreira = Barrier(nw)       

    processos = []
    for k in range(len(faixas)):
        ini, fim = faixas[k]
        p = Process(target=worker, args=(k, ini, fim, barreira, bufA, bufB, linhas, colunas, geracoes, limiar_convencimento))
        processos.append(p)

    inicio = time.perf_counter()
    # inicia os processos (todos rodam ao mesmo tempo)
    for p in processos:
        p.start()

    # espera todos os processos terminarem
    for p in processos:
        p.join()

    fim = time.perf_counter()
    tempo_total = fim - inicio

    final = bufA if geracoes % 2 == 0 else bufB
    contagem = [0] * 5
    for x in final:
        contagem[x] += 1

    total = linhas * colunas
    print("=== RESULTADO FINAL (PARALELO) ===")
    print(f"Ignorantes:      {contagem[IGNORANTE]:,} ({contagem[IGNORANTE] / total * 100:.2f}%)")
    print(f"Espalhadores:    {contagem[ESPALHADOR]:,} ({contagem[ESPALHADOR] / total * 100:.2f}%)")
    print(f"Resistentes:     {contagem[RESISTENTE]:,} ({contagem[RESISTENTE] / total * 100:.2f}%)")
    print(f"Influenciadores: {contagem[INFLUENCIADOR]:,} ({contagem[INFLUENCIADOR] / total * 100:.2f}%)")
    print(f"Inativos:        {contagem[INATIVO]:,} ({contagem[INATIVO] / total * 100:.2f}%)")
    
    print("=== RESULTADO FINAL (PARALELO) ===")
    print(f"Tempo total de execução: {tempo_total:.4f} segundos")
    print(f"Ignorantes:      {contagem[IGNORANTE]:,} ({contagem[IGNORANTE] / total * 100:.2f}%)")

if __name__ == "__main__":
    executar_paralelo(linhas=100, nw=4)