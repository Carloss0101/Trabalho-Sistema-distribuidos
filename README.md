# Simulação da Propagação de Fake News

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

As regras de transição estão implementadas na função `proxima_geracao`, no arquivo `FakeNews.py`.

## Funcionamento da simulação

A implementação atual segue estas etapas:

1. Cria uma grade e distribui aleatoriamente os estados iniciais.
2. Percorre as posições da grade e verifica os estados dos vizinhos.
3. Calcula a próxima geração em uma cópia da grade atual.
4. Conta quantas pessoas estão em cada estado.
5. Repete o processo até atingir o número de gerações definido ou até não haver mais espalhadores.

A cópia da grade evita que as alterações de uma geração interfiram nos cálculos das outras posições da mesma geração.

## Arquivos

- `FakeNews.py`: implementação da simulação sequencial, com criação da grade, regras de transição, contagem dos estados e exibição dos resultados.
- `algoritmo.txt`: descrição textual do algoritmo e de suas principais funções.

## Como executar

É necessário ter Python 3 instalado. No terminal, dentro da pasta do projeto, execute:

```bash
python FakeNews.py
```

O programa apresenta os parâmetros utilizados, a contagem dos estados a cada geração e o resumo final, incluindo o tempo de execução.

## Parâmetros

A função `executar_simulacao` permite configurar:

- `linhas` e `colunas`: dimensões da grade.
- `geracoes`: número máximo de gerações.
- `pct_espalhadores`: proporção inicial de espalhadores.
- `pct_influenciadores`: proporção inicial de influenciadores.
- `pct_resistentes`: proporção inicial de resistentes.
- `limiar_convencimento`: quantidade de vizinhos espalhadores usada nas regras de transição.
- `mostrar_grade`: define se a grade será exibida no terminal.

Os valores padrão da execução principal estão definidos no bloco `if __name__ == "__main__"` de `FakeNews.py`.

## Escopo atual

O repositório contém as implementações sequencial, paralela e distribuída da simulação de propagação de fake news. A interface gráfica documentada a seguir permite configurar e executar a versão paralela.


## Interface gráfica da versão paralela

O projeto possui uma interface gráfica desenvolvida com Python e Tkinter para facilitar a configuração e execução da simulação paralela.

A interface permite modificar os parâmetros do algoritmo antes de iniciar a execução, sem precisar alterar diretamente o código-fonte.

### Funcionalidades

- Configuração do número de linhas e colunas da matriz.
- Definição da quantidade máxima de gerações.
- Escolha da quantidade de processos paralelos.
- Configuração dos percentuais iniciais de espalhadores, influenciadores e resistentes.
- Definição do limiar de convencimento.
- Configuração da semente aleatória.
- Validação dos parâmetros informados.
- Exibição do tempo de execução e dos resultados.
- Visualização gráfica da distribuição final da população.

### Instalação das dependências

Com o Python instalado, execute na raiz do projeto:

```bash
python -m pip install -r requirements.txt
```

### Como executar

Na raiz do projeto, execute:

```bash
python Paralelo/interface.py
```

Será aberta uma janela para configurar os parâmetros e executar a simulação paralela.

Os resultados são apresentados em duas abas: Relatório e Gráfico.
