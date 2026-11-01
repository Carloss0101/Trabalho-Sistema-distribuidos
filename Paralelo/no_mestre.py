import random
from datetime import datetime
from copy import deepcopy

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


if __name__ == "__main__":
    g = criar_grade(100, 100, 42, 0.05, 0.01, 0.1)
    contagem = [0] * 5
    for linha in g:
        for c in linha:
            contagem[c] += 1
    print(contagem)