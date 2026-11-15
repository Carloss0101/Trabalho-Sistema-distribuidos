# recursos para criar a janela e seus componentes visuais.
import tkinter as tk
from tkinter import ttk, messagebox

# executa a simulação em outra thread para não travar a interface.
from threading import Thread

# permite que a thread da simulação envie resultados para a interface.
from queue import Queue, Empty

# Dá suporte ao funcionamento de aplicações que usam multiprocessing
# quando são executadas no Windows.
import multiprocessing

# Módulo responsável por executar o algoritmo paralelo.
import no_mestre

# Bibliotecas utilizadas para criar gráficos dentro da janela.
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ControladorSimulacao:

    def __init__(self, janela):
        # Guarda a janela principal da aplicação.
        self.janela = janela
        self.janela.title("Fake News Simulator")
        self.janela.geometry("850x780")
        self.janela.minsize(750, 680)

        # Dicionário que armazena os campos de entrada da interface.
        self.campos = {}

        # Fila usada para receber os resultados da thread de execução.
        self.fila = Queue()

        # Monta os componentes visuais da aplicação.
        self.criar_interface()

        # Agenda a verificação da fila para identificar quando a simulação
        # terminar e atualizar os resultados na janela.
        self.janela.after(100, self.verificar_resultado)

    def criar_interface(self):

        # Título principal da aplicação.
        titulo = ttk.Label(
            self.janela,
            text="Fake News Simulator",
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=(15, 5))

        # Identifica que esta interface controla a versão paralela.
        subtitulo = ttk.Label(
            self.janela,
            text="Controlador da Simulação Paralela"
        )
        subtitulo.pack(pady=5)

        # Área que agrupa os parâmetros configuráveis da simulação.
        configuracao = ttk.LabelFrame(
            self.janela,
            text="Configurações da simulação",
            padding=12
        )
        configuracao.pack(
            padx=25,
            pady=12,
            fill="x"
        )

        # Parâmetros disponíveis e seus valores iniciais.
        parametros = [
            ("Linhas", "linhas", "200"),
            ("Colunas", "colunas", "200"),
            ("Gerações", "geracoes", "50"),
            ("Processos paralelos", "nw", "4"),
            ("Espalhadores (%)", "pct_espalhadores", "5"),
            ("Influenciadores (%)", "pct_influenciadores", "1"),
            ("Resistentes (%)", "pct_resistentes", "10"),
            ("Limiar de convencimento", "limiar_convencimento", "2"),
            ("Semente aleatória", "seed", "1")
        ]

        # Cria um rótulo e um campo de entrada para cada parâmetro.
        # Os campos são organizados em duas colunas.
        for indice, (nome, chave, valor) in enumerate(parametros):

            linha = indice // 2
            coluna = (indice % 2) * 2

            ttk.Label(
                configuracao,
                text=nome
            ).grid(
                row=linha,
                column=coluna,
                padx=8,
                pady=7,
                sticky="w"
            )

            # StringVar permite acessar e modificar o valor digitado.
            variavel = tk.StringVar(value=valor)

            entrada = ttk.Entry(
                configuracao,
                textvariable=variavel,
                width=14
            )

            entrada.grid(
                row=linha,
                column=coluna + 1,
                padx=8,
                pady=7
            )

            # Associa o campo à sua chave para recuperar o valor depois.
            self.campos[chave] = variavel

        # Botão que inicia o processo de validação e execução.
        self.botao = ttk.Button(
            self.janela,
            text="Executar Simulação",
            command=self.iniciar_simulacao
        )
        self.botao.pack(pady=8)

        # Indicador visual exibido enquanto a simulação está em andamento.
        self.progresso = ttk.Progressbar(
            self.janela,
            mode="indeterminate",
            length=400
        )
        self.progresso.pack(pady=4)

        # Texto que informa o estado atual da execução.
        self.status = ttk.Label(
            self.janela,
            text="Aguardando execução..."
        )
        self.status.pack(pady=4)

        # Área destinada à apresentação dos resultados.
        resultado_frame = ttk.LabelFrame(
            self.janela,
            text="Resultados da simulação",
            padding=10
        )
        resultado_frame.pack(
            padx=25,
            pady=10,
            fill="both",
            expand=True
        )

        # Cria abas para separar o relatório textual do gráfico.
        self.abas = ttk.Notebook(resultado_frame)
        self.abas.pack(
            fill="both",
            expand=True
        )

        # ---------------- ABA DO RELATÓRIO ----------------

        self.aba_relatorio = ttk.Frame(self.abas)

        self.abas.add(
            self.aba_relatorio,
            text="Relatório"
        )

        # Campo que apresenta os parâmetros e os resultados da simulação.
        self.resultado = tk.Text(
            self.aba_relatorio,
            font=("Consolas", 10),
            wrap="word",
            state="disabled"
        )

        # Barra de rolagem para facilitar a leitura do relatório.
        scrollbar = ttk.Scrollbar(
            self.aba_relatorio,
            orient="vertical",
            command=self.resultado.yview
        )

        self.resultado.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.resultado.pack(
            side="left",
            fill="both",
            expand=True
        )

        # --- ABA DO GRÁFICO ---

        self.aba_grafico = ttk.Frame(self.abas)

        self.abas.add(
            self.aba_grafico,
            text="Gráfico"
        )

        # Cria a figura e o espaço onde o gráfico será desenhado.
        self.figura = Figure(
            figsize=(8, 5),
            dpi=100
        )

        self.eixo = self.figura.add_subplot(111)

        #integra o gráfico do Matplotlib à janela do Tkinter.
        self.canvas = FigureCanvasTkAgg(
            self.figura,
            master=self.aba_grafico
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        #exibe mensagens iniciais antes da primeira execução.
        self.mostrar_grafico_inicial()
        self.mostrar_resultado(
            "Os resultados aparecerão aqui após a execução."
        )

    def obter_parametros(self):

        # Recupera os valores digitados em todos os campos.
        valores = {
            chave: campo.get().strip()
            for chave, campo in self.campos.items()
        }

        # Converte os parâmetros que devem ser números inteiros.
        linhas = int(valores["linhas"])
        colunas = int(valores["colunas"])
        geracoes = int(valores["geracoes"])
        nw = int(valores["nw"])
        limiar = int(valores["limiar_convencimento"])
        seed = int(valores["seed"])

        # Converte os percentuais para números decimais.
        # A substituição permite aceitar tanto ponto quanto vírgula.
        pct_espalhadores = float(
            valores["pct_espalhadores"].replace(",", ".")
        )

        pct_influenciadores = float(
            valores["pct_influenciadores"].replace(",", ".")
        )

        pct_resistentes = float(
            valores["pct_resistentes"].replace(",", ".")
        )

        percentuais = [
            pct_espalhadores,
            pct_influenciadores,
            pct_resistentes
        ]

        # Verifica se as dimensões da matriz são válidas.
        if linhas <= 0 or colunas <= 0:
            raise ValueError(
                "Linhas e colunas devem ser maiores que zero."
            )

        # Exige pelo menos uma geração para executar a simulação.
        if geracoes <= 0:
            raise ValueError(
                "Informe pelo menos uma geração."
            )

        # A quantidade de processos não pode ser maior que o número de linhas.
        if nw <= 0 or nw > linhas:
            raise ValueError(
                "A quantidade de processos deve estar entre 1 e o número de linhas."
            )

        # O limiar representa a quantidade mínima de vizinhos espalhadores
        # necessária para convencer uma célula ignorante.
        if limiar < 1 or limiar > 8:
            raise ValueError(
                "O limiar deve estar entre 1 e 8."
            )

        # Verifica se cada percentual está entre 0 e 100.
        if any(p < 0 or p > 100 for p in percentuais):
            raise ValueError(
                "Os percentuais devem estar entre 0 e 100."
            )

        # A soma dos estados iniciais não pode ultrapassar toda a população.
        if sum(percentuais) > 100:
            raise ValueError(
                "A soma dos percentuais não pode ultrapassar 100%."
            )

        # Retorna os parâmetros no formato esperado pelo algoritmo.
        # Os percentuais são divididos por 100 para ficarem entre 0 e 1.
        return {
            "linhas": linhas,
            "colunas": colunas,
            "geracoes": geracoes,
            "nw": nw,
            "seed": seed,
            "pct_espalhadores": pct_espalhadores / 100,
            "pct_influenciadores": pct_influenciadores / 100,
            "pct_resistentes": pct_resistentes / 100,
            "limiar_convencimento": limiar
        }

    def iniciar_simulacao(self):

        # Valida os campos antes de iniciar o algoritmo.
        try:
            parametros = self.obter_parametros()
        except ValueError as erro:
            messagebox.showerror(
                "Parâmetros inválidos",
                str(erro)
            )
            return

        # Impede que o usuário inicie outra execução enquanto esta estiver ativa.
        self.botao.config(state="disabled")

        # Inicia a animação da barra de progresso.
        self.progresso.start(10)

        self.status.config(
            text="Executando simulação..."
        )

        # Informa ao usuário que o processamento começou.
        self.mostrar_resultado(
            "A simulação está sendo executada..."
        )

        # Executa o algoritmo em uma thread separada.
        # Assim, a janela continua respondendo durante o processamento.
        Thread(
            target=self.executar,
            args=(parametros,),
            daemon=True
        ).start()

    def executar(self, parametros):

        try:
            # Chama a função principal do algoritmo paralelo,
            # enviando todos os parâmetros configurados na interface.
            resultado = no_mestre.executar_paralelo(
                **parametros
            )

            # Envia o resultado para a fila, que será consultada pela janela.
            self.fila.put((
                "sucesso",
                {
                    "resultado": resultado,
                    "parametros": parametros
                }
            ))

        except Exception as erro:
            # Caso ocorra algum erro, envia sua descrição para a interface.
            self.fila.put(("erro", str(erro)))

    def verificar_resultado(self):

        # Tenta obter uma mensagem enviada pela thread de execução.
        try:
            tipo, dados = self.fila.get_nowait()

        except Empty:
            # Se ainda não houver resultado, agenda uma nova verificação.
            self.janela.after(
                100,
                self.verificar_resultado
            )
            return

        # Quando recebe uma resposta, encerra a barra de progresso
        # e libera novamente o botão de execução.
        self.progresso.stop()
        self.botao.config(state="normal")

        if tipo == "erro":

            self.status.config(
                text="Falha na execução."
            )

            messagebox.showerror(
                "Erro na simulação",
                dados
            )

        else:

            resultado = dados["resultado"]
            parametros = dados["parametros"]

            if resultado is None:

                self.status.config(
                    text="Simulação finalizada sem resultados."
                )

                messagebox.showerror(
                    "Erro",
                    "O algoritmo não retornou resultados."
                )

            else:

                self.status.config(
                    text="Simulação concluída com sucesso!"
                )

                # Apresenta os dados em formato de relatório.
                self.exibir_resultado(
                    resultado,
                    parametros
                )

                # Atualiza o gráfico com a distribuição final dos estados.
                self.atualizar_grafico(resultado)

        # Mantém a verificação ativa para as próximas execuções.
        self.janela.after(
            100,
            self.verificar_resultado
        )

    def exibir_resultado(self, resultado, parametros):

        # Organiza os parâmetros utilizados e os dados obtidos
        # em um relatório textual.
        texto = (
            "CONFIGURAÇÕES UTILIZADAS\n"
            "================================\n\n"

            f"Tamanho da matriz: "
            f"{parametros['linhas']} x {parametros['colunas']}\n"

            f"População total: "
            f"{parametros['linhas'] * parametros['colunas']:,}\n"

            f"Gerações máximas: "
            f"{parametros['geracoes']}\n"

            f"Processos paralelos: "
            f"{parametros['nw']}\n"

            f"Espalhadores iniciais: "
            f"{parametros['pct_espalhadores'] * 100:.2f}%\n"

            f"Influenciadores iniciais: "
            f"{parametros['pct_influenciadores'] * 100:.2f}%\n"

            f"Resistentes iniciais: "
            f"{parametros['pct_resistentes'] * 100:.2f}%\n"

            f"Limiar de convencimento: "
            f"{parametros['limiar_convencimento']}\n"

            f"Semente aleatória: "
            f"{parametros['seed']}\n\n"

            "RESULTADOS DA SIMULAÇÃO\n"
            "================================\n\n"

            f"Geração final: "
            f"{resultado['geracao_final']}\n"

            f"Tempo de execução: "
            f"{resultado['tempo_total']:.4f} segundos\n\n"

            "RESULTADOS DA POPULAÇÃO\n"
            "--------------------------------\n"
        )

        # Percorre os estados finais e calcula a participação percentual
        # de cada um em relação ao total da população.
        for nome, quantidade in resultado["contagem"].items():

            percentual = (
                quantidade / resultado["total"]
            ) * 100

            texto += (
                f"\n{nome}: {quantidade:,}"
                f" ({percentual:.2f}%)"
            )

        texto += "\n\n================================\n"

        # Atualiza a área de relatório da interface.
        self.mostrar_resultado(texto)

    def atualizar_grafico(self, resultado):

        # Recupera as quantidades finais de cada estado.
        contagem = resultado["contagem"]
        total = resultado["total"]

        nomes = list(contagem.keys())
        quantidades = list(contagem.values())

        # Define uma cor para representar cada estado da população.
        cores_por_estado = {
            "Ignorantes": "#64748b",
            "Espalhadores": "#ef4444",
            "Inativos": "#94a3b8",
            "Influenciadores": "#8b5cf6",
            "Resistentes": "#eab308"
        }

        cores = [
            cores_por_estado[nome]
            for nome in nomes
        ]

        # Limpa o gráfico anterior antes de desenhar o novo.
        self.eixo.clear()

        # Cria um gráfico de barras horizontais.
        barras = self.eixo.barh(
            nomes,
            quantidades,
            color=cores
        )

        # Organiza a ordem dos estados no eixo vertical.
        self.eixo.invert_yaxis()

        self.eixo.set_title(
            "Distribuição final da população",
            fontsize=13,
            fontweight="bold"
        )

        self.eixo.set_xlabel(
            "Quantidade de pessoas"
        )

        # Ajusta o limite horizontal para reservar espaço
        # para os valores apresentados ao lado das barras.
        maior_valor = max(quantidades)

        self.eixo.set_xlim(
            0,
            max(1, maior_valor * 1.30)
        )

        # Adiciona a quantidade e o percentual ao lado de cada barra.
        for barra, quantidade in zip(barras, quantidades):

            percentual = quantidade / total * 100

            self.eixo.text(
                barra.get_width() + maior_valor * 0.02,
                barra.get_y() + barra.get_height() / 2,
                f"{quantidade:,} ({percentual:.2f}%)",
                va="center",
                fontsize=9
            )

        # Ajusta o espaçamento dos elementos e atualiza a exibição.
        self.figura.tight_layout()
        self.canvas.draw_idle()

    def mostrar_grafico_inicial(self):

        # Exibe uma mensagem enquanto ainda não existe uma simulação concluída.
        self.eixo.text(
            0.5,
            0.5,
            "O gráfico aparecerá aqui após a execução.",
            ha="center",
            va="center",
            transform=self.eixo.transAxes
        )

        # Oculta os eixos enquanto nao há dados para apresentar.
        self.eixo.set_axis_off()

        self.canvas.draw()

    def mostrar_resultado(self, texto):

        # Habilita temporariamente o campo para substituir seu conteúdo.
        self.resultado.config(state="normal")

        # Remove o relatório anterior.
        self.resultado.delete(
            "1.0",
            tk.END
        )

        # Insere o texto atualizado.
        self.resultado.insert(
            tk.END,
            texto
        )

        # Bloqueia a edição manual do relatório.
        self.resultado.config(state="disabled")


if __name__ == "__main__":

    # Prepara o suporte a multiprocessing no Windows.
    multiprocessing.freeze_support()

    # Cria a janela principal e inicia a aplicação.
    janela = tk.Tk()
    aplicacao = ControladorSimulacao(janela)
    janela.mainloop()