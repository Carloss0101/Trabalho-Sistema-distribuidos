# Bibliotecas utilizadas para criar e controlar a interface.
import tkinter as tk
from tkinter import ttk, messagebox

# Bibliotecas para iniciar e controlar os processos da rede.
import subprocess
import socket
import sys
import os

# Permite localizar os arquivos do projeto independentemente
# da pasta em que o terminal foi aberto.
from pathlib import Path

# Permite acompanhar a saída do mestre sem bloquear a janela.
from threading import Thread
from queue import Queue, Empty


class InterfaceDistribuida:

    def __init__(self, janela):

        # Configurações da janela principal.
        self.janela = janela
        self.janela.title("Fake News Simulator")
        self.janela.geometry("850x780")
        self.janela.minsize(750, 680)

        # Identifica a pasta que contém os arquivos broker.py,
        # worker.py e master.py.
        self.diretorio_nodes = Path(__file__).resolve().parent / "nodes"

        # Referências para controlar os processos da rede.
        self.processo_broker = None
        self.processos_workers = []
        self.processo_master = None

        # Fila utilizada para receber as mensagens do processo mestre.
        self.fila = Queue()

        # Identifica cada execução para ignorar mensagens antigas
        # quando uma simulação for cancelada.
        self.execucao_id = 0
        self.execucao_ativa = False

        # Guarda os campos de configuração da interface.
        self.campos = {}

        # Monta os componentes visuais.
        self.criar_interface()

        # Define o comportamento ao fechar a janela.
        self.janela.protocol(
            "WM_DELETE_WINDOW",
            self.ao_fechar
        )

        # Inicia a verificação periódica das mensagens recebidas.
        self.janela.after(
            100,
            self.processar_fila
        )

    def criar_interface(self):

        # Título principal.
        titulo = ttk.Label(
            self.janela,
            text="Fake News Simulator",
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=(15, 5))

        # Identifica a versão do algoritmo controlada pela interface.
        subtitulo = ttk.Label(
            self.janela,
            text="Controlador da Simulação Distribuída"
        )
        subtitulo.pack(pady=5)

        # Área destinada às configurações.
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

        # Parâmetros que podem ser alterados antes da execução.
        parametros = [
            ("Linhas", "linhas", "100"),
            ("Colunas", "colunas", "100"),
            ("Gerações", "geracoes", "50"),
            ("Quantidade de workers", "workers", "4"),
            ("Espalhadores (%)", "pct_espalhadores", "5"),
            ("Influenciadores (%)", "pct_influenciadores", "1"),
            ("Resistentes (%)", "pct_resistentes", "10"),
            ("Limiar de convencimento", "limiar", "2")
        ]

        # Cria os campos de entrada e organiza em duas colunas.
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

            # Armazena o valor digitado em uma variável.
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

        # Opção para imprimir a matriz durante a execução.
        # Por padrão, fica desativada para evitar uma saída muito extensa.
        self.mostrar_grade = tk.BooleanVar(value=False)

        check_grade = ttk.Checkbutton(
            configuracao,
            text="Mostrar grade a cada geração",
            variable=self.mostrar_grade
        )

        check_grade.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=8,
            pady=8,
            sticky="w"
        )

        # Informação sobre o funcionamento da rede.
        informacao = ttk.Label(
            self.janela,
            text=(
                "O broker e os workers serão iniciados automaticamente "
                "para cada execução."
            ),
            wraplength=750
        )
        informacao.pack(pady=5)

        # Área que agrupa os botões de controle.
        botoes = ttk.Frame(self.janela)
        botoes.pack(pady=8)

        # Inicia a validação e a execução da simulação.
        self.botao_iniciar = ttk.Button(
            botoes,
            text="Iniciar Simulação",
            command=self.iniciar_simulacao
        )
        self.botao_iniciar.pack(
            side="left",
            padx=8
        )

        # Permite interromper a execução e encerrar os processos.
        self.botao_parar = ttk.Button(
            botoes,
            text="Parar Simulação",
            command=self.parar_simulacao,
            state="disabled"
        )
        self.botao_parar.pack(
            side="left",
            padx=8
        )

        # Indicador visual de execução.
        self.progresso = ttk.Progressbar(
            self.janela,
            mode="indeterminate",
            length=400
        )
        self.progresso.pack(pady=5)

        # Mostra o estado atual da aplicação.
        self.status = tk.StringVar(
            value="Aguardando execução..."
        )

        status_label = ttk.Label(
            self.janela,
            textvariable=self.status
        )
        status_label.pack(pady=5)

        # Área destinada aos registros e resultados.
        resultado_frame = ttk.LabelFrame(
            self.janela,
            text="Execução e resultados",
            padding=10
        )
        resultado_frame.pack(
            padx=25,
            pady=10,
            fill="both",
            expand=True
        )

        # Campo de texto que recebe as mensagens impressas pelo master.
        self.saida = tk.Text(
            resultado_frame,
            font=("Consolas", 9),
            wrap="word",
            state="disabled"
        )

        # Barra de rolagem para consultar toda a saída.
        scrollbar = ttk.Scrollbar(
            resultado_frame,
            orient="vertical",
            command=self.saida.yview
        )

        self.saida.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.saida.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Mensagem inicial da área de resultados.
        self.adicionar_log(
            "Configure os parâmetros e clique em Iniciar Simulação.\n"
        )

    def obter_parametros(self):

        # Recupera os valores digitados nos campos.
        valores = {
            chave: campo.get().strip()
            for chave, campo in self.campos.items()
        }

        # Converte os parâmetros inteiros.
        linhas = int(valores["linhas"])
        colunas = int(valores["colunas"])
        geracoes = int(valores["geracoes"])
        workers = int(valores["workers"])
        limiar = int(valores["limiar"])

        # Converte os percentuais para números decimais.
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

        # Exige pelo menos uma geração.
        if geracoes <= 0:
            raise ValueError(
                "Informe pelo menos uma geração."
            )

        # Exige pelo menos um worker e impede criar mais workers
        # do que células disponíveis na matriz.
        if workers <= 0 or workers > linhas * colunas:
            raise ValueError(
                "A quantidade de workers deve ser válida para a matriz."
            )

        # O limiar de convencimento deve respeitar a vizinhança de Moore.
        if limiar < 1 or limiar > 8:
            raise ValueError(
                "O limiar deve estar entre 1 e 8."
            )

        # Verifica os limites individuais dos percentuais.
        if any(p < 0 or p > 100 for p in percentuais):
            raise ValueError(
                "Os percentuais devem estar entre 0 e 100."
            )

        # A soma dos percentuais não pode ultrapassar a população.
        if sum(percentuais) > 100:
            raise ValueError(
                "A soma dos percentuais não pode ultrapassar 100%."
            )

        # Retorna os parâmetros validados.
        return {
            "linhas": linhas,
            "colunas": colunas,
            "geracoes": geracoes,
            "workers": workers,
            "pct_espalhadores": pct_espalhadores,
            "pct_influenciadores": pct_influenciadores,
            "pct_resistentes": pct_resistentes,
            "limiar": limiar,
            "mostrar_grade": self.mostrar_grade.get()
        }

    def verificar_porta(self):

        # Verifica se a porta utilizada pelo broker está disponível.
        # Isso evita iniciar uma segunda rede na mesma porta.
        teste = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            teste.bind(("localhost", 5555))
            return True

        except OSError:
            return False

        finally:
            teste.close()

    def iniciar_simulacao(self):

        # Valida os parâmetros antes de iniciar os processos.
        try:
            parametros = self.obter_parametros()

        except ValueError as erro:
            messagebox.showerror(
                "Parâmetros inválidos",
                str(erro)
            )
            return

        # Confirma se a pasta com os arquivos da rede existe.
        if not self.diretorio_nodes.exists():
            messagebox.showerror(
                "Erro",
                "A pasta Distribuido/nodes não foi encontrada."
            )
            return

        # Impede conflitos com outra execução que esteja utilizando
        # a porta fixa do broker.
        if not self.verificar_porta():
            messagebox.showerror(
                "Rede indisponível",
                "A porta 5555 já está em uso.\n"
                "Verifique se existe outra execução do projeto aberta."
            )
            return

        # Cria um identificador para esta execução.
        self.execucao_id += 1
        identificador = self.execucao_id

        self.execucao_ativa = True

        # Bloqueia o botão de iniciar e libera o botão de parar.
        self.botao_iniciar.config(state="disabled")
        self.botao_parar.config(state="normal")

        # Inicia o indicador de processamento.
        self.progresso.start(10)

        self.status.set("Iniciando a rede distribuída...")

        # Limpa as mensagens da execução anterior.
        self.limpar_log()

        self.adicionar_log(
            "INICIANDO SIMULAÇÃO DISTRIBUÍDA\n"
            "========================================\n\n"
        )

        # Primeiro inicia o broker.
        try:
            self.processo_broker = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    "broker.py"
                ],
                cwd=str(self.diretorio_nodes),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.adicionar_log(
                "Broker iniciado na porta 5555.\n"
            )

        except Exception as erro:
            self.falha_inicializacao(
                identificador,
                f"Não foi possível iniciar o broker: {erro}"
            )
            return

        # Aguarda o broker iniciar antes de abrir os workers.
        self.janela.after(
            800,
            lambda: self.iniciar_workers(
                parametros,
                identificador
            )
        )

    def iniciar_workers(self, parametros, identificador):

        # Ignora o agendamento caso a execução tenha sido cancelada.
        if identificador != self.execucao_id or not self.execucao_ativa:
            return

        # Verifica se o broker continua ativo.
        if (
            self.processo_broker is None or
            self.processo_broker.poll() is not None
        ):
            self.falha_inicializacao(
                identificador,
                "O broker foi encerrado antes da entrada dos workers."
            )
            return

        self.status.set("Iniciando os workers...")

        # Cria a quantidade de processos workers definida pelo usuário.
        try:
            for numero in range(parametros["workers"]):

                processo = subprocess.Popen(
                    [
                        sys.executable,
                        "-u",
                        "worker.py"
                    ],
                    cwd=str(self.diretorio_nodes),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                self.processos_workers.append(processo)

                self.adicionar_log(
                    f"Worker {numero + 1} iniciado.\n"
                )

        except Exception as erro:
            self.falha_inicializacao(
                identificador,
                f"Não foi possível iniciar os workers: {erro}"
            )
            return

        # Aguarda os workers se registrarem no broker.
        self.status.set(
            "Aguardando o registro dos workers no broker..."
        )

        self.janela.after(
            1500,
            lambda: self.iniciar_master(
                parametros,
                identificador
            )
        )

    def iniciar_master(self, parametros, identificador):

        # Verifica se a execução continua válida.
        if identificador != self.execucao_id or not self.execucao_ativa:
            return

        # Confirma se o broker continua funcionando.
        if (
            self.processo_broker is None or
            self.processo_broker.poll() is not None
        ):
            self.falha_inicializacao(
                identificador,
                "O broker foi encerrado durante a inicialização."
            )
            return

        # Verifica se todos os workers continuam ativos.
        workers_encerrados = [
            processo
            for processo in self.processos_workers
            if processo.poll() is not None
        ]

        if workers_encerrados:
            self.falha_inicializacao(
                identificador,
                "Um ou mais workers foram encerrados durante a inicialização."
            )
            return

        self.status.set("Executando o algoritmo distribuído...")

        self.adicionar_log(
            "\nTodos os workers foram iniciados.\n"
            "Iniciando o processo master...\n\n"
        )

        # O master recebe os parâmetros pela linha de comando.
        # A ordem segue exatamente o que master.py espera:
        # linhas, colunas, gerações, influenciadores,
        # espalhadores, resistentes, limiar e mostrar grade.
        argumentos = [
            sys.executable,
            "-u",
            "master.py",
            str(parametros["linhas"]),
            str(parametros["colunas"]),
            str(parametros["geracoes"]),
            str(parametros["pct_influenciadores"] / 100),
            str(parametros["pct_espalhadores"] / 100),
            str(parametros["pct_resistentes"] / 100),
            str(parametros["limiar"]),
            "1" if parametros["mostrar_grade"] else "0"
        ]

        try:
            # Define UTF-8 para que os acentos sejam exibidos
            # corretamente na saída do processo no Windows.
            ambiente = os.environ.copy()
            ambiente["PYTHONIOENCODING"] = "utf-8"

            # Inicia o master e captura tudo o que ele imprimir.
            self.processo_master = subprocess.Popen(
                argumentos,
                cwd=str(self.diretorio_nodes),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=ambiente
            )

            # A leitura da saída acontece em outra thread para
            # que a interface continue respondendo.
            Thread(
                target=self.acompanhar_master,
                args=(
                    self.processo_master,
                    identificador
                ),
                daemon=True
            ).start()

        except Exception as erro:
            self.falha_inicializacao(
                identificador,
                f"Não foi possível iniciar o master: {erro}"
            )

    def acompanhar_master(self, processo, identificador):

        # Lê cada linha impressa pelo master e envia para a fila.
        # O processamento visual acontece na thread principal.
        if processo.stdout is not None:

            for linha in processo.stdout:
                self.fila.put((
                    "log",
                    identificador,
                    linha
                ))

        # Aguarda o encerramento do master e captura seu código de saída.
        codigo_saida = processo.wait()

        self.fila.put((
            "fim",
            identificador,
            codigo_saida
        ))

    def processar_fila(self):

        # Verifica se existem novas mensagens enviadas pela thread.
        try:
            while True:

                tipo, identificador, conteudo = self.fila.get_nowait()

                # Ignora mensagens de execuções anteriores.
                if identificador != self.execucao_id:
                    continue

                if tipo == "log":

                    # Apresenta as mensagens do master na janela.
                    self.adicionar_log(conteudo)

                elif tipo == "fim":

                    # Trata o encerramento da simulação.
                    self.finalizar_simulacao(conteudo)

        except Empty:
            pass

        # Agenda a próxima verificação.
        self.janela.after(
            100,
            self.processar_fila
        )

    def finalizar_simulacao(self, codigo_saida):

        # Evita processar um encerramento duplicado.
        if not self.execucao_ativa:
            return

        self.execucao_ativa = False

        # Para a barra de progresso.
        self.progresso.stop()

        # Garante que processos que não tenham sido encerrados
        # pelo master sejam finalizados.
        self.encerrar_processos()

        # Restaura os botões da interface.
        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")

        if codigo_saida == 0:

            self.status.set(
                "Simulação distribuída concluída!"
            )

            self.adicionar_log(
                "\nSIMULAÇÃO FINALIZADA COM SUCESSO.\n"
            )

        else:

            self.status.set(
                "A simulação foi encerrada com erro."
            )

            self.adicionar_log(
                f"\nO processo master terminou com código {codigo_saida}.\n"
            )

            messagebox.showerror(
                "Erro na simulação",
                "O processo master foi encerrado com erro.\n"
                "Consulte as mensagens exibidas na interface."
            )

    def falha_inicializacao(self, identificador, mensagem):

        # Evita tratar falhas de uma execução já cancelada.
        if identificador != self.execucao_id:
            return

        self.execucao_ativa = False

        # Invalida possíveis mensagens que ainda estejam na fila.
        self.execucao_id += 1

        # Encerra os processos que chegaram a ser iniciados.
        self.encerrar_processos()

        self.progresso.stop()

        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")

        self.status.set("Falha ao iniciar a simulação.")

        self.adicionar_log(
            f"\nERRO: {mensagem}\n"
        )

        messagebox.showerror(
            "Falha na inicialização",
            mensagem
        )

    def parar_simulacao(self):

        # Não faz nada se não houver uma execução ativa.
        if not self.execucao_ativa:
            return

        self.execucao_ativa = False

        # Invalida mensagens que possam chegar da execução interrompida.
        self.execucao_id += 1

        # Encerra o master, os workers e o broker.
        self.encerrar_processos()

        self.progresso.stop()

        self.botao_iniciar.config(state="normal")
        self.botao_parar.config(state="disabled")

        self.status.set("Simulação interrompida pelo usuário.")

        self.adicionar_log(
            "\nSIMULAÇÃO INTERROMPIDA.\n"
        )

    def encerrar_processo(self, processo):

        # Encerra um processo apenas quando ele ainda estiver ativo.
        if processo is None or processo.poll() is not None:
            return

        processo.terminate()

        # Aguarda o encerramento e força a finalização caso necessário.
        try:
            processo.wait(timeout=1)

        except subprocess.TimeoutExpired:
            processo.kill()
            processo.wait(timeout=1)

    def encerrar_processos(self):

        # Primeiro encerra o master.
        self.encerrar_processo(
            self.processo_master
        )

        # Depois encerra todos os workers.
        for processo in self.processos_workers:
            self.encerrar_processo(processo)

        # Por último, encerra o broker.
        self.encerrar_processo(
            self.processo_broker
        )

        # Limpa as referências dos processos.
        self.processo_master = None
        self.processos_workers = []
        self.processo_broker = None

    def adicionar_log(self, mensagem):

        # Habilita o campo para inserir novas mensagens.
        self.saida.config(state="normal")

        self.saida.insert(
            tk.END,
            mensagem
        )

        # Mantém a rolagem posicionada na mensagem mais recente.
        self.saida.see(tk.END)

        # Bloqueia a edição manual da área de saída.
        self.saida.config(state="disabled")

    def limpar_log(self):

        # Remove as mensagens da execução anterior.
        self.saida.config(state="normal")

        self.saida.delete(
            "1.0",
            tk.END
        )

        self.saida.config(state="disabled")

    def ao_fechar(self):

        # Encerra todos os processos antes de fechar a janela.
        self.execucao_ativa = False
        self.execucao_id += 1

        self.encerrar_processos()

        self.janela.destroy()


if __name__ == "__main__":

    # Cria a janela e inicia a interface gráfica.
    janela = tk.Tk()

    aplicacao = InterfaceDistribuida(janela)

    janela.mainloop()