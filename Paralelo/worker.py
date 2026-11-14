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

def worker(k, ini, fim, barreira, bufA, bufB, linhas, colunas, geracoes, limiar, mudancas, geracao_parada):
    atual, proximo = bufA, bufB

    for g in range(geracoes):
        teve_mudanca = 0 

        for i in range(ini, fim):
            for j in range(colunas):

                #quarda estado atual da celula
                indice = i * colunas + j
                estado_atual = atual[indice]

                #calculo da proxima geracao e salva em proximo
                novo_estado = nova_celula(atual, i, j, linhas, colunas, limiar)
                proximo[indice] = novo_estado

                #em caso de mudança, troca pra 1
                if novo_estado != estado_atual:
                    teve_mudanca = 1

        #anota alteracao(0 ou 1)
        mudancas[k] = teve_mudanca

        #espera todos os workers terminarem a geracao antes de continuar
        barreira.wait()

        #se nao houve mudanca, para a simulacao e anota a geracao que parou
        if sum(mudancas) == 0:
            if k == 0:
                geracao_parada.value = g + 1
            break 

        atual, proximo = proximo, atual