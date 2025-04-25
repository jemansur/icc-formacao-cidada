import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
import pandas as pd

logo_path = "c84616cb-25bb-448d-9739-31c9e21c4178.png"

st.title("Índice de Contribuição Cidadã (ICC)")
nome = st.text_input("Seu nome:")
tema = st.text_input("Temática da pesquisa:")

criterios = [
    "Promoção da equidade e inclusão",
    "Estímulo à participação democrática",
    "Desenvolvimento do pensamento crítico",
    "Integração com problemas reais da sociedade",
    "Uso ético e consciente das tecnologias",
    "Valorização de identidades e culturas diversas",
    "Empatia e diálogo",
    "Consciência socioambiental",
    "Direitos humanos e justiça social",
    "Engajamento comunitário e responsabilidade coletiva",
    "Cidadania digital"
]

st.markdown("### Defina os pesos dos critérios — a soma deve totalizar exatamente 10")
pesos_usuario = {}
for crit in criterios:
    pesos_usuario[crit] = st.number_input(f"Peso - {crit}", min_value=0.1, max_value=2.0, value=1.0, step=0.1)

def converter_nota(nota):
    return {4: 1.0, 3: 0.75, 2: 0.5, 1: 0.25}.get(nota, 0)

def interpretar_icc(valor):
    if valor >= 0.85:
        return "Excelente contribuição para a formação cidadã e a diversidade social."
    elif valor >= 0.7:
        return "Boa contribuição, com potencial de fortalecimento em alguns critérios."
    elif valor >= 0.5:
        return "Contribuição regular, recomenda-se revisão e reforço em múltiplas dimensões."
    else:
        return "Baixa contribuição; é necessário reestruturar a proposta para ampliar o impacto cidadão."

class RelatorioICC(FPDF):
    def header(self):
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 30)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Grupo de Pesquisa Cidadania e Diversidade Social", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, "Centro Universitário UniCarioca Digital", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)

    def chapter_body(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, text)
        self.ln()

notas_usuario = {}
with st.form("form_icc"):
    for criterio in criterios:
        notas_usuario[criterio] = st.selectbox(
            criterio,
            options=[4, 3, 2, 1],
            format_func=lambda x: f"{x} - " + {4: "Excelente", 3: "Bom", 2: "Regular", 1: "Insuficiente"}[x]
        )
    
    total_pesos = sum(pesos_usuario.values())
    st.markdown(f"**Soma atual dos pesos: {total_pesos:.2f}**")
    if total_pesos < 10:
        st.warning("A soma dos pesos está abaixo de 10.")
    elif total_pesos > 10:
        st.error("A soma dos pesos está acima de 10. Ajuste para continuar.")
    submitted = st.form_submit_button("Calcular ICC") if total_pesos == 10 else False
    

if submitted and nome and tema:
    numerador = 0
    denominador = 0
    notas_convertidas = {}

    for criterio in criterios:
        nota_convertida = converter_nota(notas_usuario[criterio])
        peso = pesos_usuario[criterio]
        notas_convertidas[criterio] = nota_convertida
        numerador += nota_convertida * peso
        denominador += peso

    icc = numerador / denominador
    interpretacao = interpretar_icc(icc)

    st.success(f"ICC de {nome} sobre '{tema}': {icc:.3f}")
    st.info(interpretacao)
    st.progress(icc)

    st.markdown("### Visualização por Critério")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(notas_convertidas.values()),
        theta=list(notas_convertidas.keys()),
        fill='toself',
        name='Desempenho'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Pesos aplicados por critério")
    df_pesos = pd.DataFrame({
        "Critério": criterios,
        "Peso": [pesos_usuario[c] for c in criterios],
        "Nota atribuída": [notas_usuario[c] for c in criterios],
        "Nota convertida": [notas_convertidas[c] for c in criterios]
    })
    st.dataframe(df_pesos)

    radar_labels = list(notas_convertidas.keys())
    radar_vals = list(notas_convertidas.values())
    radar_vals.append(radar_vals[0])
    radar_labels.append(radar_labels[0])
    fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(radar_vals, linewidth=1, linestyle='solid')
    ax.fill(radar_vals, 'b', alpha=0.1)
    ax.set_xticks([i * 2 * 3.14159 / len(radar_labels) for i in range(len(radar_labels))])
    ax.set_xticklabels(radar_labels, fontsize=8)
    radar_path = "/tmp/grafico_icc_peso_radar.png"
    plt.savefig(radar_path)
    plt.close()

    pdf = RelatorioICC()
    pdf.add_page()
    pdf.chapter_title("Dados da Avaliação")
    pdf.chapter_body(f"Nome: {nome}\nTemática da pesquisa: {tema}")
    pdf.chapter_body(f"ICC: {icc:.3f}\n\nInterpretação: {interpretacao}")
    pdf.chapter_title("Notas e Pesos por Critério:")
    for crit in criterios:
        pdf.chapter_body(f"- {crit}: Nota {notas_usuario[crit]}, Peso {pesos_usuario[crit]}")
    pdf.chapter_title("Gráfico de Desempenho")
    pdf.image(radar_path, x=30, w=150)
    pdf_path = "/tmp/relatorio_icc_com_peso.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Baixar Relatório PDF com Pesos", f, file_name="relatorio_icc_com_peso.pdf")