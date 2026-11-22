# Simulação da Propagação de Fake News

https://github.com/Carloss0101/Trabalho-Sistema-distribuidos

## Sobre o projeto

Este projeto simula a propagação de notícias falsas em uma população representada por uma matriz bidimensional. Cada posição da matriz representa uma pessoa, e seu estado pode mudar de acordo com a situação dos vizinhos ao longo das gerações.

A simulação utiliza a vizinhança de Moore: para cada posição, são considerados os até oito vizinhos que ficam ao redor dela, sem incluir a própria posição.

## Estados da população

| Estado | Descrição |
| --- | --- |
| Ignorante | Pessoa que ainda não está compartilhando a notícia falsa. |
| Espalhador | Pessoa que compartilha a notícia falsa. |
| Inativo | Pessoa que recebeu a informação, mas não continua espalhando. |
| Influenciador | Estado que representa uma pessoa com maior influência na propagação. |
| Resistente | Pessoa inicialmente resistente à notícia falsa. |

## Funcionamento da simulação

A implementação atual segue estas etapas:

1. Cria uma grade e distribui aleatoriamente os estados iniciais.
2. Percorre as posições da grade e verifica os estados dos vizinhos.
3. Calcula a próxima geração em uma cópia da grade atual.
4. Conta quantas pessoas estão em cada estado.
5. Repete o processo até atingir o número de gerações definido ou até não haver mais espalhadores.

A cópia da grade evita que as alterações de uma geração interfiram nos cálculos das outras posições da mesma geração.

## Parâmetros

A função `executar_simulacao` permite configurar:

- `linhas` e `colunas`: dimensões da grade.
- `geracoes`: número máximo de gerações.
- `pct_espalhadores`: proporção inicial de espalhadores.
- `pct_influenciadores`: proporção inicial de influenciadores.
- `pct_resistentes`: proporção inicial de resistentes.
- `limiar_convencimento`: quantidade de vizinhos espalhadores usada nas regras de transição.
- `mostrar_grade`: define se a grade será exibida no terminal.

## Requisitos

`python3.15` e sua versão free-threaded `python3.15t`

`matplotlib` para montagem dos gráficos finais na interface

## Como executar a versão Sequencial

Vá até o diretório `Sequencial` e execute
```bash
python3.15 FakeNews.py <count_lin> <count_col> <count_ger> <pct_inf> <pct_esp> <pct_res> <limiar>
```

## Como executar a versão Paralela

Vá até o diretório `Paralelo` e execute
```bash
python3.15 no_mestre.py <count_lin> <count_col> <count_ger> <pct_inf> <pct_esp> <pct_res> <limiar> 
```

ou 

```bash
python3.15 interface.py 
```

para executar através da interface gráfica

## Como executar a versão Paralela

Vá até o diretório `Distribuido/nodes` e execute

```bash
./init.sh 
```

ou execute, em sequência:

```bash
python3.15 broker.py &
```

```bash
python3.15 worker.py &    **para quantos workers forem existir na rede**
```

```bash
PYTHON_GIL=0 python3.15t master.py <count_lin> <count_col> <count_ger> <pct_inf> <pct_esp> <pct_res> <limiar> <mostrar_grade>
```

ou 

```bash
python 3.15 ../interface.py
```

para executar através da interface gráfica