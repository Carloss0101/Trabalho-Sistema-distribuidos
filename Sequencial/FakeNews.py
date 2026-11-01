import random
import time
from datetime import datetime
from copy import deepcopy
# o deepcopy garante independência, as alterações em objetos 
# aninhados não afetam o original

IGNORANTE = 0
ESPALHADOR = 1
INATIVO = 2
INFLUENCIADOR = 3
RESISTENTE = 4

def criar_grade(
    linhas, 
    colunas, 
    pct_espalhadores=0.02, 
    pct_influenciadores=0.01, 
    pct_resistentes=0.1):

    random.seed(datetime.now().timestamp())

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

def contar_vizinhos(grade, i, j):
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

            if 0 <= ni < len(grade) and 0 <= nj < len(grade[0]):
                vizinhos[grade[ni][nj]] += 1

    return vizinhos

def proxima_geracao(grade, limiar_convencimento=2):
    nova_grade = deepcopy(grade)

    for i in range(len(grade)):
        for j in range(len(grade[i])):

            vizinhos = contar_vizinhos(grade, i, j)

            if grade[i][j] == IGNORANTE:
                if (vizinhos[ESPALHADOR] >= limiar_convencimento or 
                    vizinhos[INFLUENCIADOR] >= 1):
                    nova_grade[i][j] = ESPALHADOR

            elif grade[i][j] == ESPALHADOR:
                if (vizinhos[ESPALHADOR] >= limiar_convencimento and 
                    vizinhos[INFLUENCIADOR] >= 1):
                    nova_grade[i][j] = INFLUENCIADOR
                else:
                    nova_grade[i][j] = INATIVO

            elif grade[i][j] == INFLUENCIADOR:
                if (not vizinhos[IGNORANTE]  and 
                    not vizinhos[ESPALHADOR] and 
                    not vizinhos[RESISTENTE]):
                    nova_grade[i][j] = INATIVO

            elif grade[i][j] == RESISTENTE:
            	if (vizinhos[ESPALHADOR] >= limiar_convencimento and 
                    vizinhos[INFLUENCIADOR] >= 1):
            		nova_grade[i][j] = ESPALHADOR

    return nova_grade

def contar_estados(grade):
    contagem = {
        IGNORANTE:     0,
        ESPALHADOR:    0,
        INATIVO:       0,
        INFLUENCIADOR: 0,
        RESISTENTE:    0
    }

    for linha in grade:
        for celula in linha:
            contagem[celula] += 1

    return contagem


def imprimir_grade(grade, limite=30):
    simbolos = {
        IGNORANTE:     '.',
        ESPALHADOR:    'E',
        INATIVO:       'N',
        INFLUENCIADOR: 'I',
        RESISTENTE:    'R'
    }

    linhas  = min(len(grade),    limite)
    colunas = min(len(grade[0]), limite)

    for i in range(linhas):
        linha = ""
        for j in range(colunas):
            linha += simbolos[grade[i][j]] + " "
        print(linha)
    print()


def executar_simulacao(
    linhas=100,
    colunas=100,
    geracoes=50,
    pct_influenciadores=0.01,
    pct_espalhadores=0.02,
	pct_resistentes=0.1,
    limiar_convencimento=2,
    mostrar_grade=False
):

    grade = criar_grade(
        linhas,
        colunas,
        pct_espalhadores,
        pct_influenciadores,
        pct_resistentes
    )

    print("=== SIMULAÇÃO SEQUENCIAL DE PROPAGAÇÃO DE FAKE NEWS ===")
    print("=======================================================")
    print(f"Tamanho da grade: {linhas} x {colunas} ({linhas*colunas:,}) pessoas)")
    print(f"Gerações: {geracoes}")
    contagem_inicial = contar_estados(grade)
    print(
        f"Percentual inicial de espalhadores: "
        f"{pct_espalhadores * 100:.2f}% "
        f"({contagem_inicial[ESPALHADOR]:,} espalhadores reais)"
    )
    print(f"Limiar de convencimento: {limiar_convencimento} vizinhos")
    print("=======================================================")
    print()

    inicio = datetime.now().timestamp()

    for geracao in range(geracoes):
        grade = proxima_geracao(grade, limiar_convencimento)

        contagem = contar_estados(grade)

        print(f'''
            ------------------------
            Geração {geracao + 1:03d}
            Ignorantes:      {contagem[IGNORANTE]:,}
            Espalhadores:    {contagem[ESPALHADOR]:,}
            Resistentes:     {contagem[RESISTENTE]:,}
            Influenciadores: {contagem[INFLUENCIADOR]:,}
            Inativos:        {contagem[INATIVO]:,}
            ------------------------
        ''')

        if mostrar_grade: imprimir_grade(grade)

        if not contagem[ESPALHADOR]:
            print("\nA propagação terminou: não há mais espalhadores.")
            break

    fim = datetime.now().timestamp()

    tempo_total = fim - inicio

    print()
    print("=== RESULTADO FINAL ===")
    print("=======================")
    print(f"Tempo total de execução: {tempo_total:.4f} segundos")

    contagem_final = contar_estados(grade)
    total = linhas * colunas

    print(f"Ignorantes finais: {contagem_final[IGNORANTE]:,} ({contagem_final[IGNORANTE] / total * 100:,.2f}%)")
    print(f"Espalhadores finais: {contagem_final[ESPALHADOR]:,} ({contagem_final[ESPALHADOR] / total * 100:,.2f}%)")
    print(f"Resistentes finais: {contagem_final[RESISTENTE]:,} ({contagem_final[RESISTENTE] / total * 100:,.2f}%)")
    print(f"Influenciadores finais: {contagem_final[INFLUENCIADOR]:,} ({contagem_final[INFLUENCIADOR] / total * 100:,.2f}%)")
    print(f"Inativos finais: {contagem_final[INATIVO]:,} ({contagem_final[INATIVO] / total * 100:,.2f}%)")
    print("=======================\n")

if __name__ == "__main__":
    executar_simulacao(
        linhas=100,
        colunas=100,
        geracoes=50,
        pct_influenciadores=0.01,
        pct_espalhadores=0.05,
		pct_resistentes=0.1,
        limiar_convencimento=3,
        mostrar_grade=False
    )
