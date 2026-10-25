import random
import time
from copy import deepcopy
# o deepcopy garante independência, as alterações em objetos 
# aninhados não afetam o original

IGNORANTE = 0
ESPALHADOR = 1
INATIVO = 2
INFLUENCIADOR = 3
#RESISTENTE = 4

def criar_grade(linhas, colunas, percentual_espalhadores=0.02, percentual_influenciadores=0.01, semente=42):
    random.seed(semente)

    grade = [[IGNORANTE for _ in range(colunas)] for _ in range(linhas)]

    total_celulas = linhas * colunas
    total_espalhadores = int(total_celulas * percentual_espalhadores)
    total_influenciadores = int(total_celulas * percentual_influenciadores)

    for _ in range(total_espalhadores):
        i = random.randint(0, linhas - 1)
        j = random.randint(0, colunas - 1)
        grade[i][j] = ESPALHADOR

    #Seta aleatoriamente os influenciadores na tabela.
    for _ in range(total_influenciadores):
        i = random.randint(0, linhas - 1)
        j = random.randint(0, colunas - 1)
        grade[i][j] = INFLUENCIADOR
    
    return grade

def contar_vizinhos(grade, i, j):
    vizinhos = {
        IGNORANTE: 0,
        ESPALHADOR: 0,
        INATIVO: 0,
        INFLUENCIADOR: 0,
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
        for j in range(len(grade[0])):

            vizinhos = contar_vizinhos(grade, i, j)
            
            if grade[i][j] == IGNORANTE:
                if vizinhos[ESPALHADOR] >= limiar_convencimento or vizinhos[INFLUENCIADOR] >= 1:
                    nova_grade[i][j] = ESPALHADOR

            elif grade[i][j] == ESPALHADOR:
                if vizinhos[ESPALHADOR] >= limiar_convencimento and vizinhos[INFLUENCIADOR] >= 1:
                    nova_grade[i][j] = INFLUENCIADOR
                else:
                    nova_grade[i][j] = INATIVO

            #Quanto não tem vizinho IGNORANTE e nem ESPALHADOR se torna inativo
            elif grade[i][j] == INFLUENCIADOR:
                if not vizinhos[IGNORANTE] and not vizinhos[ESPALHADOR]:
                    nova_grade[i][j] = INATIVO

    return nova_grade

def contar_estados(grade):
    contagem = {
        IGNORANTE: 0,
        ESPALHADOR: 0,
        INATIVO: 0,
        INFLUENCIADOR: 0,
    }

    for linha in grade:
        for celula in linha:
            contagem[celula] += 1

    return contagem


def imprimir_grade(grade, limite=30):
    simbolos = {
        IGNORANTE: ".",
        ESPALHADOR: "E",
        INATIVO: "N",
        INFLUENCIADOR: "I",
    }

    linhas = min(len(grade), limite)
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
    percentual_influenciadores=0.01,
    percentual_espalhadores=0.02,
    limiar_convencimento=2,
    mostrar_grade=False
):

    grade = criar_grade(
        linhas,
        colunas,
        percentual_espalhadores,
        percentual_influenciadores
    )

    print("=== SIMULAÇÃO SEQUENCIAL DE PROPAGAÇÃO DE FAKE NEWS ===")
    print(f"Tamanho da grade: {linhas} x {colunas} ({linhas*colunas:,}) pessoas)")
    print(f"Gerações: {geracoes}")
    contagem_inicial = contar_estados(grade)
    print(
        f"Percentual inicial de espalhadores: "
        f"{percentual_espalhadores * 100:.2f}% "
        f"({contagem_inicial[ESPALHADOR]:,} espalhadores reais)"
    )
    print(f"Limiar de convencimento: {limiar_convencimento} vizinhos")
    print()

    inicio = time.time()

    for geracao in range(geracoes):
        grade = proxima_geracao(grade, limiar_convencimento)

        contagem = contar_estados(grade)

        print(
            f"Geração {geracao + 1:03d} | "
            f"Ignorantes: {contagem[IGNORANTE]:>10,} | "
            f"Espalhadores: {contagem[ESPALHADOR]:>10,} | "
            f"Inativos: {contagem[INATIVO]:>10,} | "
            f"Influenciadores: {contagem[INFLUENCIADOR]:>10,} | "
        )

        if mostrar_grade:
            imprimir_grade(grade)

        if contagem[ESPALHADOR] == 0:
            print("\nA propagação terminou: não há mais espalhadores.")
            break

    fim = time.time()

    tempo_total = fim - inicio

    print()
    print("=== RESULTADO FINAL ===")
    print(f"Tempo total de execução: {tempo_total:.4f} segundos")

    contagem_final = contar_estados(grade)
    total = linhas * colunas

    print(f"Ignorantes finais: {contagem_final[IGNORANTE]:,} ({contagem_final[IGNORANTE] / total * 100:,.2f}%)")
    print(f"Espalhadores finais: {contagem_final[ESPALHADOR]:,} ({contagem_final[ESPALHADOR] / total * 100:,.2f}%)")
    print(f"Inativos finais: {contagem_final[INATIVO]:,} ({contagem_final[INATIVO] / total * 100:,.2f}%)")


if __name__ == "__main__":
    executar_simulacao(
        linhas=100,
        colunas=100,
        geracoes=50,
        percentual_influenciadores=0.01,
        percentual_espalhadores=0.05,
        limiar_convencimento=3,
        mostrar_grade=True
    )