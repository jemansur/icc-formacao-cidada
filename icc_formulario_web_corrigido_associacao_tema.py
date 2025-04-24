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

criterios_pesos = {
    "Promoção da equidade e inclusão": 1.2,
    "Estímulo à participação democrática": 1.0,
    "Desenvolvimento do pensamento crítico": 1.0,
    "Integração com problemas reais da sociedade": 1.0,
    "Uso ético e consciente das tecnologias": 0.8,
    "Valorização de identidades e culturas diversas": 1.0,
    "Empatia e diálogo": 0.8,
    "Consciência socioambiental": 0.6,
    "Direitos humanos e justiça social": 1.2,
    "Engajamento comunitário e responsabilidade coletiva": 0.8,
    "Cidadania digital": 0.6
}

# Atividades extraídas do documento
atividades_por_criterio = {
    "Promoção da equidade e inclusão": [
        "Adaptação de materiais didáticos para diferentes necessidades",
        "Uso de linguagem inclusiva nas comunicações escolares",
        "Formação de professores sobre práticas antidiscriminatórias",
        "Promoção de campanhas de valorização da diversidade",
        "Aplicação de avaliações com critérios inclusivos"
    ],
    "Direitos humanos e justiça social": [
        "Estudos sobre a Declaração Universal dos Direitos Humanos",
        "Debates sobre racismo, machismo, LGBTQIA+fobia",
        "Rodas de conversa sobre justiça e igualdade",
        "Oficinas sobre direitos da criança e do adolescente"
    ],
    "Consciência socioambiental": [
        "Projetos de reciclagem e reaproveitamento",
        "Campanhas de conscientização ambiental",
        "Feiras ecológicas",
        "Debates sobre mudanças climáticas"
    ]
}

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
    for criterio in criterios_pesos:
        notas_usuario[criterio] = st.selectbox(
            criterio,
            options=[4, 3, 2, 1],
            format_func=lambda x: f"{x} - " + {4: "Excelente", 3: "Bom", 2: "Regular", 1: "Insuficiente"}[x]
        )
    submitted = st.form_submit_button("Calcular ICC")

if submitted and nome and tema:
    numerador = 0
    denominador = 0
    notas_convertidas = {}

    for criterio, peso in criterios_pesos.items():
        nota_convertida = converter_nota(notas_usuario[criterio])
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

    # Filtro de atividades coerentes com a temática
    st.markdown("### Sugestões de Atividades Relacionadas à Temática da Pesquisa que possam contribuir com o ICC")
    tema_palavras = tema.lower().split()
    sugestoes_tema = []
    for crit, atividades in atividades_por_criterio.items():
        for atividade in atividades:
            if any(palavra in atividade.lower() for palavra in tema_palavras):
                sugestoes_tema.append((crit, atividade))

    if sugestoes_tema:
        df_sugestoes = pd.DataFrame(sugestoes_tema, columns=["Critério", "Atividade"])
        st.dataframe(df_sugestoes)
    else:
        st.warning("Não foram encontradas sugestões diretamente ligadas à temática digitada.")

    # PDF
    radar_labels = list(notas_convertidas.keys())
    radar_vals = list(notas_convertidas.values())
    radar_vals.append(radar_vals[0])
    radar_labels.append(radar_labels[0])
    fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(radar_vals, linewidth=1, linestyle='solid')
    ax.fill(radar_vals, 'b', alpha=0.1)
    ax.set_xticks([i * 2 * 3.14159 / len(radar_labels) for i in range(len(radar_labels))])
    ax.set_xticklabels(radar_labels, fontsize=8)
    radar_path = "/tmp/grafico_icc_radar.png"
    plt.savefig(radar_path)
    plt.close()

    pdf = RelatorioICC()
    pdf.add_page()
    pdf.chapter_title("Dados da Avaliação")
    pdf.chapter_body(f"Nome: {nome}\nTemática da pesquisa: {tema}")
    pdf.chapter_body(f"ICC: {icc:.3f}\n\nInterpretação: {interpretacao}")
    pdf.chapter_title("Notas por Critério:")
    for crit, nota in notas_usuario.items():
        pdf.chapter_body(f"- {crit}: Nota {nota}")
    pdf.chapter_title("Gráfico de Desempenho")
    pdf.image(radar_path, x=30, w=150)
    if sugestoes_tema:
        pdf.chapter_title("Sugestões de Atividades Relacionadas à Temática")
        for crit, atividade in sugestoes_tema:
            pdf.chapter_body(f"{crit}: {atividade}")
    pdf_path = "/tmp/relatorio_icc_sugestoes_tema.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Baixar Relatório PDF Completo", f, file_name="relatorio_icc_sugestoes_tema.pdf")