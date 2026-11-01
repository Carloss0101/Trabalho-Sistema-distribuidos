def worker(k, ini, fim, barreira):
    print(f"worker {k}: cuida das linhas {ini} a {fim - 1}")
    barreira.wait()
    print(f"worker {k}: passou da barreira")