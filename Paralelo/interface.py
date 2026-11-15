
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue, Empty
import multiprocessing

import no_mestre

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ControladorSimulacao:

    def __init__(self, janela):

        self.janela = janela
        self.janela.title("Fake News Simulator")
        self.janela.geometry("850x780")
        self.janela.minsize(750, 680)

        self.campos = {}
        self.fila = Queue()

        self.criar_interface()

        self.janela.after(100, self.verificar_resultado)

    def criar_interface(self):

        # Título
        titulo = ttk.Label(
            self.janela,
            text="Fake News Simulator",
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=(15, 5))

        subtitulo = ttk.Label(
            self.janela,
            text="Controlador da Simulação Paralela"
        )
        subtitulo.pack(pady=5)

        # Configurações
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

        # Criação dos campos de configuração
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

            self.campos[chave] = variavel

        # Botão executar
        self.botao = ttk.Button(
            self.janela,
            text="Executar Simulação",
            command=self.iniciar_simulacao
        )
        self.botao.pack(pady=8)

        # Barra de progresso
        self.progresso = ttk.Progressbar(
            self.janela,
            mode="indeterminate",
            length=400
        )
        self.progresso.pack(pady=4)

        # Status
        self.status = ttk.Label(
            self.janela,
            text="Aguardando execução..."
        )
        self.status.pack(pady=4)

        # Área de resultados com abas
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

        self.abas = ttk.Notebook(resultado_frame)
        self.abas.pack(
            fill="both",
            expand=True
        )

        # Aba do relatório
        self.aba_relatorio = ttk.Frame(self.abas)

        self.abas.add(
            self.aba_relatorio,
            text="Relatório"
        )

        self.resultado = tk.Text(
            self.aba_relatorio,
            font=("Consolas", 10),
            wrap="word",
            state="disabled"
        )

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

        # Aba do gráfico
        self.aba_grafico = ttk.Frame(self.abas)

        self.abas.add(
            self.aba_grafico,
            text="Gráfico"
        )

        self.figura = Figure(
            figsize=(8, 5),
            dpi=100
        )

        self.eixo = self.figura.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figura,
            master=self.aba_grafico
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        self.mostrar_grafico_inicial()

        self.mostrar_resultado(
            "Os resultados aparecerão aqui após a execução."
        )

    def obter_parametros(self):

        valores = {
            chave: campo.get().strip()
            for chave, campo in self.campos.items()
        }

        # Conversão dos valores
        linhas = int(valores["linhas"])
        colunas = int(valores["colunas"])
        geracoes = int(valores["geracoes"])
        nw = int(valores["nw"])
        limiar = int(valores["limiar_convencimento"])
        seed = int(valores["seed"])

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

        # Validações
        if linhas <= 0 or colunas <= 0:
            raise ValueError(
                "Linhas e colunas devem ser maiores que zero."
            )

        if geracoes <= 0:
            raise ValueError(
                "Informe pelo menos uma geração."
            )

        if nw <= 0 or nw > linhas:
            raise ValueError(
                "A quantidade de processos deve estar entre 1 e o número de linhas."
            )

        if limiar < 1 or limiar > 8:
            raise ValueError(
                "O limiar deve estar entre 1 e 8."
            )

        if any(p < 0 or p > 100 for p in percentuais):
            raise ValueError(
                "Os percentuais devem estar entre 0 e 100."
            )

        if sum(percentuais) > 100:
            raise ValueError(
                "A soma dos percentuais não pode ultrapassar 100%."
            )

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

        try:
            parametros = self.obter_parametros()

        except ValueError as erro:
            messagebox.showerror(
                "Parâmetros inválidos",
                str(erro)
            )
            return

        self.botao.config(state="disabled")

        self.progresso.start(10)

        self.status.config(
            text="Executando simulação..."
        )

        self.mostrar_resultado(
            "A simulação está sendo executada..."
        )

        Thread(
            target=self.executar,
            args=(parametros,),
            daemon=True
        ).start()

    def executar(self, parametros):

        try:
            resultado = no_mestre.executar_paralelo(
                **parametros
            )

            self.fila.put((
                "sucesso",
                {
                    "resultado": resultado,
                    "parametros": parametros
                }
            ))

        except Exception as erro:
            self.fila.put(("erro", str(erro)))

    def verificar_resultado(self):

        try:
            tipo, dados = self.fila.get_nowait()

        except Empty:
            self.janela.after(
                100,
                self.verificar_resultado
            )
            return

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

                self.exibir_resultado(
                    resultado,
                    parametros
                )

                self.atualizar_grafico(resultado)

        self.janela.after(
            100,
            self.verificar_resultado
        )

    def exibir_resultado(self, resultado, parametros):

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

        for nome, quantidade in resultado["contagem"].items():

            percentual = (
                quantidade / resultado["total"]
            ) * 100

            texto += (
                f"\n{nome}: {quantidade:,}"
                f" ({percentual:.2f}%)"
            )

        texto += "\n\n================================\n"

        self.mostrar_resultado(texto)

    def atualizar_grafico(self, resultado):

        contagem = resultado["contagem"]
        total = resultado["total"]

        nomes = list(contagem.keys())
        quantidades = list(contagem.values())

        # Cores para os estados
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

        # Limpa o gráfico anterior
        self.eixo.clear()

        # Cria o gráfico de barras
        barras = self.eixo.barh(
            nomes,
            quantidades,
            color=cores
        )

        self.eixo.invert_yaxis()

        self.eixo.set_title(
            "Distribuição final da população",
            fontsize=13,
            fontweight="bold"
        )

        self.eixo.set_xlabel(
            "Quantidade de pessoas"
        )

        maior_valor = max(quantidades)

        self.eixo.set_xlim(
            0,
            max(1, maior_valor * 1.30)
        )

        # Exibe quantidade e percentual em cada barra
        for barra, quantidade in zip(barras, quantidades):

            percentual = quantidade / total * 100

            self.eixo.text(
                barra.get_width() + maior_valor * 0.02,
                barra.get_y() + barra.get_height() / 2,
                f"{quantidade:,} ({percentual:.2f}%)",
                va="center",
                fontsize=9
            )

        self.figura.tight_layout()

        # Atualiza o gráfico na janela
        self.canvas.draw_idle()

    def mostrar_grafico_inicial(self):

        self.eixo.text(
            0.5,
            0.5,
            "O gráfico aparecerá aqui após a execução.",
            ha="center",
            va="center",
            transform=self.eixo.transAxes
        )

        self.eixo.set_axis_off()

        self.canvas.draw()

    def mostrar_resultado(self, texto):

        self.resultado.config(state="normal")

        self.resultado.delete(
            "1.0",
            tk.END
        )

        self.resultado.insert(
            tk.END,
            texto
        )

        self.resultado.config(state="disabled")


if __name__ == "__main__":

    multiprocessing.freeze_support()

    janela = tk.Tk()

    aplicacao = ControladorSimulacao(janela)

    janela.mainloop()
