import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def calcular_amortizacao(valor_casa, entrada, taxa_juros_anual, prazo_anos, seguro_mensal=0.0, comissao_inicial=0.0):
    valor_financiado = valor_casa - entrada
    meses = prazo_anos * 12
    taxa_mensal = (taxa_juros_anual / 100) / 12

    prestacoes = []
    saldo = valor_financiado

    if taxa_mensal > 0:
        prestacao_base = valor_financiado * (taxa_mensal * (1 + taxa_mensal) ** meses) / ((1 + taxa_mensal) ** meses - 1)
    else:
        prestacao_base = valor_financiado / meses

    for mes in range(1, meses + 1):
        juros_mes = saldo * taxa_mensal
        capital_mes = prestacao_base - juros_mes
        saldo -= capital_mes
        prestacoes.append({
            "Mês": mes,
            "Ano": (mes - 1) // 12 + 1,
            "Prestação (€)": prestacao_base,
            "Juros (€)": juros_mes,
            "Capital (€)": capital_mes,
            "Saldo Devedor (€)": saldo if saldo > 0 else 0
        })

    return pd.DataFrame(prestacoes), prestacao_base


# --- INTERFACE Streamlit ---
st.set_page_config(page_title="Simulador Crédito Habitação", layout="centered")
st.title("🏠 Simulador de Crédito Habitação")

valor_casa = st.number_input("Valor da casa (€)", min_value=0.0, value=200000.0, step=1000.0)
entrada = st.number_input("Entrada inicial (€)", min_value=0.0, value=40000.0, step=1000.0)
taxa_juros_anual = st.number_input("Taxa de juro anual (%)", min_value=0.0, value=2.0, step=0.1)
prazo_anos = st.slider("Prazo do empréstimo (anos)", 5, 40, 30)
seguro_mensal = st.number_input("Seguro mensal (€)", min_value=0.0, value=30.0)
comissao_inicial = st.number_input("Comissão inicial (€)", min_value=0.0, value=1000.0)

if st.button("Simular"):
    df, prestacao_base = calcular_amortizacao(valor_casa, entrada, taxa_juros_anual, prazo_anos, seguro_mensal, comissao_inicial)

    juros_total = df["Juros (€)"].sum()
    capital_total = df["Capital (€)"].sum()
    total_pago = capital_total + juros_total + (seguro_mensal * prazo_anos * 12) + comissao_inicial

    st.subheader("📊 Resumo")
    st.write(f"**Montante financiado:** €{valor_casa - entrada:,.2f}")
    st.write(f"**Prestação mensal base:** €{prestacao_base:,.2f}")
    st.write(f"**Total pago (com seguro e comissão):** €{total_pago:,.2f}")

    # Tabela mensal
    st.subheader("📅 Breakdown Mensal")
    st.dataframe(df.style.format({"Prestação (€)": "€{:.2f}", "Juros (€)": "€{:.2f}", "Capital (€)": "€{:.2f}", "Saldo Devedor (€)": "€{:.2f}"}), use_container_width=True)

    # Totais por ano
    st.subheader("📆 Resumo Anual")
    resumo_anual = df.groupby("Ano")[["Juros (€)", "Capital (€)"]].sum().reset_index()
    resumo_anual["Total (€)"] = resumo_anual["Juros (€)"] + resumo_anual["Capital (€)"]
    st.dataframe(resumo_anual.style.format("€{:.2f}"), use_container_width=True)

    # Gráfico
    st.subheader("📈 Gráfico: Juros vs Capital")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Mês"], df["Juros (€)"], label="Juros", color="red")
    ax.plot(df["Mês"], df["Capital (€)"], label="Capital", color="green")
    ax.set_title("Evolução da Prestação")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Valor (€)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # EXPORTAÇÃO PARA EXCEL - coloca isto DENTRO do bloco do botão
    from io import BytesIO

    st.subheader("📤 Exportar simulação para Excel")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Mensal', index=False)
        resumo_anual.to_excel(writer, sheet_name='Resumo Anual', index=False)

        workbook = writer.book
        format_currency = workbook.add_format({'num_format': '€#,##0.00'})

        for sheet in ['Mensal', 'Resumo Anual']:
            worksheet = writer.sheets[sheet]
            worksheet.set_column('A:Z', 18, format_currency)

    output.seek(0)
    st.download_button(
        label="📥 Baixar Excel com Simulação",
        data=output,
        file_name='simulador_credito_habitacao.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
