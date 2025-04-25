import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

# Base de temáticas com palavras-chave
tematicas_semantico = {
    "educação antirracista": {
        "gatilhos": ["racismo", "racial", "etnia", "afro", "preto", "negritude", "preconceito", "discriminação", "antirracista"],
        "atividades": [
            "Rodas de conversa sobre identidade racial",
            "Produção de murais antirracistas",
            "Análise de livros com protagonistas negros",
            "Debates sobre racismo estrutural",
            "Oficinas de contação de histórias afro-brasileiras",
            "Criação de podcasts sobre igualdade racial"
        ]
    }
}

logo_path = "c84616cb-25bb-448d-9739-31c9e21c4178.png"

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

def converter_nota(nota):
    return {4: 1.0, 3: 0.75, 2: 0.5, 1: 0.25}[nota]

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

# Interface do app
st.title("ICC com Associação Semântica")
nome = st.text_input("Seu nome:")
tema = st.text_input("Temática da pesquisa:")

pesos_usuario = {}
notas_usuario = {}

with st.form("avaliacao_icc"):
    for crit in criterios:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{crit}**")
        with col2:
            pesos_usuario[crit] = st.number_input(f"Peso", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key=f"peso_{crit}")
        with col3:
            notas_usuario[crit] = st.selectbox("Nota", [4, 3, 2, 1], key=f"nota_{crit}")
    enviado = st.form_submit_button("Calcular ICC")

if enviado and nome and tema:
    numerador, denominador = 0, 0
    notas_convertidas = {}
    for crit in criterios:
        nota = converter_nota(notas_usuario[crit])
        peso = pesos_usuario[crit]
        notas_convertidas[crit] = nota
        numerador += nota * peso
        denominador += peso

    icc = numerador / denominador
    st.success(f"ICC de {nome}: {icc:.3f}")
    st.info(interpretar_icc(icc))

    # Sugestões por associação semântica
    tema_detectado = None
    atividades_sugeridas = []

    for tema_ref, dados in tematicas_semantico.items():
        if any(gatilho in tema.lower() for gatilho in dados["gatilhos"]):
            tema_detectado = tema_ref
            atividades_sugeridas = dados["atividades"]
            break

    st.markdown("### Sugestões de Atividades Associadas")
    if atividades_sugeridas:
        df_sug = pd.DataFrame({"Atividades sugeridas": atividades_sugeridas})
        st.dataframe(df_sug)
    else:
        st.warning("Nenhuma associação semântica encontrada para a temática digitada.")

    # Gráfico radar
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(notas_convertidas.values()),
        theta=criterios,
        fill='toself',
        name='Desempenho'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
    st.plotly_chart(fig)

    # Gerar PDF
    radar_vals = list(notas_convertidas.values()) + [list(notas_convertidas.values())[0]]
    radar_labels = criterios + [criterios[0]]
    fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(radar_vals, linewidth=1, linestyle='solid')
    ax.fill(radar_vals, 'b', alpha=0.1)
    ax.set_xticks([i * 2 * 3.14159 / len(radar_labels) for i in range(len(radar_labels))])
    ax.set_xticklabels(radar_labels, fontsize=8)
    radar_path = "/tmp/grafico_icc_semantico.png"
    plt.savefig(radar_path)
    plt.close()

    pdf = RelatorioICC()
    pdf.add_page()
    pdf.chapter_title("Dados da Avaliação")
    pdf.chapter_body(f"Nome: {nome}\nTemática: {tema}")
    pdf.chapter_body(f"ICC: {icc:.3f}\n{interpretar_icc(icc)}")
    pdf.chapter_title("Notas e Pesos por Critério")
    for crit in criterios:
        pdf.chapter_body(f"- {crit}: Nota {notas_usuario[crit]}, Peso {pesos_usuario[crit]}")
    pdf.chapter_title("Gráfico de Desempenho")
    pdf.image(radar_path, x=30, w=150)
    pdf.chapter_title("Sugestões de Atividades Associadas")
    if atividades_sugeridas:
        for atividade in atividades_sugeridas:
            pdf.chapter_body(f"- {atividade}")
    else:
        pdf.chapter_body("Nenhuma associação semântica encontrada para a temática.")
    pdf_path = "/tmp/relatorio_icc_semantico.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Baixar Relatório PDF", f, file_name="relatorio_icc_semantico.pdf")