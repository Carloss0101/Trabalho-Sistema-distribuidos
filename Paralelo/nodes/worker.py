def contar_vizinhos(buf, i, j, L, C):
    """Vizinhança de Moore sobre vetor linear. Usa L e C da grade INTEIRA,
    por isso o worker consegue ler linhas de faixas vizinhas."""
    cont = [0] * 5
    for ni in range(max(0, i - 1), min(L, i + 2)):
        base = ni * C
        for nj in range(max(0, j - 1), min(C, j + 2)):
            if ni == i and nj == j:
                continue
            cont[buf[base + nj]] += 1
    return cont


def regra(estado, v, limiar):
    """Mesma regra de transição do código sequencial, como função pura."""
    if estado == IGNORANTE:
        if v[ESPALHADOR] >= limiar or v[INFLUENCIADOR] >= 1:
            return ESPALHADOR
    elif estado == ESPALHADOR:
        if v[ESPALHADOR] >= limiar and v[INFLUENCIADOR] >= 1:
            return INFLUENCIADOR
        return INATIVO
    elif estado == INFLUENCIADOR:
        if not v[IGNORANTE] and not v[ESPALHADOR] and not v[RESISTENTE]:
            return INATIVO
    elif estado == RESISTENTE:
        if v[ESPALHADOR] >= limiar and v[INFLUENCIADOR] >= 1:
            return ESPALHADOR
    return estado

