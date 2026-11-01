import random
from multiprocessing import RawArray, Process, Barrier
from worker import worker

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

#Dividir as linhas entre os workers
def dividir_linhas(linhas, workers):
    base, resto = divmod(linhas, workers)
    faixas = []
    ini = 0

    for k in range(workers):
        tamanho = base + (1 if k < resto else 0)
        fim = ini + tamanho
        faixas.append((ini, fim))
        ini = fim #Proxima faixa começa quando essa termina.
    return faixas

def executar_paralelo(linhas=100, colunas=100, nw=4, seed=42,
                      pct_espalhadores=0.05, pct_influenciadores=0.01,
                      pct_resistentes=0.1):
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
        p = Process(target=worker, args=(k, ini, fim, barreira))
        processos.append(p)

    # inicia os processos (todos rodam ao mesmo tempo)
    for p in processos:
        p.start()

    # espera todos os processos terminarem
    for p in processos:
        p.join()

if __name__ == "__main__":
    executar_paralelo(linhas=100, nw=4)