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

Os arquivos presentes neste repositório incluem a implementação sequencial descrita acima. Qualquer implementação paralela ou distribuída deverá ser documentada separadamente quando estiver disponível.
