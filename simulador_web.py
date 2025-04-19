import streamlit as st
st.set_page_config(page_title="Simulador Crédito Habitação", page_icon="🏡", layout="centered")

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import plotly.graph_objects as go



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

def calcular_taeg(montante, prazo_anos, custo_total):
    # Aproximação da TAEG: custo total anual dividido pelo montante financiado
    taeg = ((custo_total / (montante * prazo_anos)) * 100)
    return taeg



# TÍTULO
st.title("🏡 Simulador e Comparador de Crédito Habitação")
st.markdown("Simula prestações e compara diferentes condições entre dois bancos.")
st.markdown("---")


# ⬇️ Simulação única
st.subheader("🧮 Simulação Individual")

col1, col2 = st.columns(2)
with col1:
    valor_casa = st.number_input("💰 Valor da casa (€)", min_value=0.0, value=200000.0)
    entrada = st.number_input("🏦 Entrada (€)", min_value=0.0, value=40000.0)
    seguro_mensal = st.number_input("🛡️ Seguro mensal (€)", min_value=0.0, value=30.0)
with col2:
    taxa = st.number_input("📉 Taxa juro anual (%)", min_value=0.0, value=2.0)
    prazo = st.slider("📆 Prazo do empréstimo (anos)", 5, 40, 30)
    comissao = st.number_input("💼 Comissão inicial (€)", min_value=0.0, value=1000.0)

if st.button("Simular"):
    df, prestacao_base = calcular_amortizacao(valor_casa, entrada, taxa, prazo, seguro_mensal, comissao)
    juros_total = df["Juros (€)"].sum()
    capital_total = df["Capital (€)"].sum()
    total_pago = capital_total + juros_total + (seguro_mensal * prazo * 12) + comissao
    taeg = calcular_taeg(valor_casa - entrada, prazo, total_pago)
    


    st.subheader("📊 Resumo")
    st.write(f"**Montante financiado:** €{valor_casa - entrada:,.2f}")
    st.write(f"**Prestação mensal base:** €{prestacao_base:,.2f}")
    st.write(f"**Total pago (com seguro e comissão):** €{total_pago:,.2f}")
    st.write(f"**TAEG estimada:** {taeg:.2f}%")

    st.subheader("📅 Breakdown Mensal")
    st.dataframe(df.style.format("€{:.2f}"), use_container_width=True)

    st.subheader("📆 Resumo Anual")
    resumo_anual = df.groupby("Ano")[["Juros (€)", "Capital (€)"]].sum().reset_index()
    resumo_anual["Total (€)"] = resumo_anual["Juros (€)"] + resumo_anual["Capital (€)"]
    st.dataframe(resumo_anual.style.format("€{:.2f}"), use_container_width=True)


    st.subheader("📈 Gráfico: Evolução da Prestação")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Juros (€)"], mode='lines', name='Juros', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Capital (€)"], mode='lines', name='Capital', line=dict(color='green')))

    fig.update_layout(
        title="Juros vs Capital ao Longo do Tempo",
        xaxis_title="Mês",
        yaxis_title="Valor (€)",
        legend_title="Composição da Prestação",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 Distribuição dos Custos Totais")

    pie_fig = go.Figure(data=[go.Pie(
        labels=['Juros', 'Capital', 'Seguros', 'Comissão'],
        values=[
            juros_total,
            capital_total,
            seguro_mensal * prazo * 12,
            comissao
        ],
        hole=0.4,
        marker=dict(colors=["red", "green", "blue", "orange"]),
        textinfo='label+percent',
        hoverinfo='label+value'
    )])

    pie_fig.update_layout(
        title_text="Distribuição Total do Crédito",
        template="plotly_white"
    )

    st.plotly_chart(pie_fig, use_container_width=True)



    # Excel
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


# 🏦 Comparação
st.markdown("---")
st.subheader("📊 Comparação entre dois bancos")

tab1, tab2 = st.tabs(["Banco A", "Banco B"])

with tab1:
    st.markdown("### Parâmetros Banco A")
    col1, col2 = st.columns(2)
    with col1:
        vcA = st.number_input("Valor casa (A)", value=200000.0, key="vcA")
        entradaA = st.number_input("Entrada (A)", value=40000.0, key="entA")
        segA = st.number_input("Seguro mensal (A)", value=30.0, key="segA")
    with col2:
        txA = st.number_input("Taxa juro anual (A)", value=2.0, key="txA")
        prazoA = st.slider("Prazo (A)", 5, 40, 30, key="przA")
        comA = st.number_input("Comissão (A)", value=1000.0, key="comA")

with tab2:
    st.markdown("### Parâmetros Banco B")
    col1, col2 = st.columns(2)
    with col1:
        vcB = st.number_input("Valor casa (B)", value=200000.0, key="vcB")
        entradaB = st.number_input("Entrada (B)", value=40000.0, key="entB")
        segB = st.number_input("Seguro mensal (B)", value=30.0, key="segB")
    with col2:
        txB = st.number_input("Taxa juro anual (B)", value=2.2, key="txB")
        prazoB = st.slider("Prazo (B)", 5, 40, 30, key="przB")
        comB = st.number_input("Comissão (B)", value=1000.0, key="comB")

if st.button("Comparar Bancos"):
    dfA, prestA = calcular_amortizacao(vcA, entradaA, txA, prazoA, segA, comA)
    dfB, prestB = calcular_amortizacao(vcB, entradaB, txB, prazoB, segB, comB)

    totalA = prestA * prazoA * 12 + comA + segA * prazoA * 12
    totalB = prestB * prazoB * 12 + comB + segB * prazoB * 12
    taegA = calcular_taeg(vcA - entradaA, prazoA, totalA)
    taegB = calcular_taeg(vcB - entradaB, prazoB, totalB)
    jurosA = dfA["Juros (€)"].sum()
    jurosB = dfB["Juros (€)"].sum()

    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### 🏦 Banco A")
        st.write(f"Prestação: **€{prestA:,.2f}**")
        st.write(f"Total em juros: **€{jurosA:,.2f}**")
        st.write(f"Total pago: **€{totalA:,.2f}**")
        st.write(f"TAEG estimada: **{taegA:.2f}%**") 

    with colB:
        st.markdown("#### 🏦 Banco B")
        st.write(f"Prestação: **€{prestB:,.2f}**")
        st.write(f"Total em juros: **€{jurosB:,.2f}**")
        st.write(f"Total pago: **€{totalB:,.2f}**")
        st.write(f"TAEG estimada: **{taegB:.2f}%**")

    st.subheader("📊 Comparação Visual entre Bancos")

    barras = go.Figure(data=[
        go.Bar(name='Banco A', x=['Prestação Mensal', 'Total Juros', 'Total Pago'], y=[prestA, jurosA, totalA],
            marker_color='teal'),
        go.Bar(name='Banco B', x=['Prestação Mensal', 'Total Juros', 'Total Pago'], y=[prestB, jurosB, totalB],
            marker_color='goldenrod')
    ])

    barras.update_layout(
        barmode='group',
        title="Comparativo de Custos e Prestações",
        yaxis_title="Valor (€)",
        template="plotly_white"
    )

    st.plotly_chart(barras, use_container_width=True)
