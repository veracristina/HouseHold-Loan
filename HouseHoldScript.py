import matplotlib.pyplot as plt

def calcular_amortizacao(valor_casa, entrada, taxa_juros_anual, prazo_anos, seguro_mensal=0.0, comissao_inicial=0.0):
    valor_financiado = valor_casa - entrada
    meses = prazo_anos * 12
    taxa_mensal = (taxa_juros_anual / 100) / 12

    prestacoes = []
    juros_total = 0
    capital_total = 0

    if taxa_mensal > 0:
        prestacao_base = valor_financiado * (taxa_mensal * (1 + taxa_mensal) ** meses) / ((1 + taxa_mensal) ** meses - 1)
    else:
        prestacao_base = valor_financiado / meses

    saldo = valor_financiado

    for mes in range(1, meses + 1):
        juros_mes = saldo * taxa_mensal
        capital_mes = prestacao_base - juros_mes
        saldo -= capital_mes

        prestacoes.append({
            "mês": mes,
            "juros": juros_mes,
            "capital": capital_mes,
            "prestacao": prestacao_base,
            "saldo": saldo
        })

        juros_total += juros_mes
        capital_total += capital_mes

    custo_total = (prestacao_base + seguro_mensal) * meses + comissao_inicial

    # --- Resumo ---
    print(f"\n🔍 Resumo:")
    print(f"Valor da casa: €{valor_casa:,.2f}")
    print(f"Entrada inicial: €{entrada:,.2f}")
    print(f"Montante financiado: €{valor_financiado:,.2f}")
    print(f"Prestação mensal base: €{prestacao_base:,.2f}")
    print(f"Seguro mensal: €{seguro_mensal:,.2f}")
    print(f"Comissão inicial: €{comissao_inicial:,.2f}")
    print(f"Total em juros: €{juros_total:,.2f}")
    print(f"Total pago (incluindo seguro e comissões): €{custo_total:,.2f}")

    return prestacoes


def mostrar_grafico_amortizacao(prestacoes):
    meses = [p["mês"] for p in prestacoes]
    juros = [p["juros"] for p in prestacoes]
    capital = [p["capital"] for p in prestacoes]

    plt.figure(figsize=(10, 6))
    plt.plot(meses, juros, label="Juros", color="red")
    plt.plot(meses, capital, label="Amortização de Capital", color="green")
    plt.title("Evolução da Prestação (Capital vs Juros)")
    plt.xlabel("Mês")
    plt.ylabel("Valor (€)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# --- Entradas ---
valor_casa = float(input("🏠 Valor da casa (€): "))
entrada = float(input("💰 Entrada inicial (€): "))
taxa_juros_anual = float(input("📉 Taxa de juro anual (%): "))
prazo_anos = int(input("📆 Prazo do empréstimo (anos): "))
seguro_mensal = float(input("🛡️ Seguro mensal (€): "))
comissao_inicial = float(input("💼 Comissão inicial (€): "))

# --- Cálculo ---
prestacoes = calcular_amortizacao(valor_casa, entrada, taxa_juros_anual, prazo_anos, seguro_mensal, comissao_inicial)

# --- Gráfico ---
mostrar_grafico_amortizacao(prestacoes)
