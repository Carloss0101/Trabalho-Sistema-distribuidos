## Dependências

```bash
python 3.15+ e python3.15t+
matplotlib
```
---
Para verificar se possui `python3.15` na máquina e qual sua versão, execute
```bash
python3.15 --version 
```
Caso não possua, instale com 
```bash
sudo dnf install python3.15
```
ou
```bash
sudo apt install python3.15
```
---
Para verificar se possui a versão free-threaded `python3.15t`, execute
```bash
python3.15t --version
```
Caso não possua, instale com 
```bash
sudo dnf install python3.15-freethreading
```
ou
```bash
sudo apt install python3.15-freethreading
```
---
Para instalar `matplotlib` através do pip, execute
```bash
pip install matplotlib
```
ou
```bash
pip3 install matplotlib
```

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

## Como executar a versão Distribuída

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