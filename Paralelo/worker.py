from constantes import *

def contar_vizinhos(buf, i, j, linhas, colunas):
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

            if 0 <= ni < linhas and 0 <= nj < colunas:
                vizinhos[buf[ni * colunas + nj]] += 1

    return vizinhos

#aplica as regras para calcular a proxima geração
def nova_celula(buf, i, j, linhas, colunas, limiar):
    estado = buf[i * colunas + j]
    viz = contar_vizinhos(buf, i, j, linhas, colunas)

    if estado == IGNORANTE:
        if viz[ESPALHADOR] >= limiar or viz[INFLUENCIADOR] >= 1:
            return ESPALHADOR

    elif estado == ESPALHADOR:
        if viz[ESPALHADOR] >= limiar and viz[INFLUENCIADOR] >= 1:
            return INFLUENCIADOR
        return INATIVO

    elif estado == INFLUENCIADOR:
        if viz[IGNORANTE] == 0 and viz[ESPALHADOR] == 0 and viz[RESISTENTE] == 0:
            return INATIVO

    elif estado == RESISTENTE:
        if viz[ESPALHADOR] >= limiar and viz[INFLUENCIADOR] >= 1:
            return ESPALHADOR

    return estado  

def worker(k, ini, fim, barreira, bufA, bufB, linhas, colunas, geracoes, limiar):
    atual, proximo = bufA, bufB

    for g in range(geracoes):
        for i in range(ini, fim):
            for j in range(colunas):
                proximo[i * colunas + j] = nova_celula(atual, i, j, linhas, colunas, limiar)

        barreira.wait()
        atual, proximo = proximo, atual