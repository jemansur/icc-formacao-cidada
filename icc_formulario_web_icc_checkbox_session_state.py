import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path

logo_path = "c84616cb-25bb-448d-9739-31c9e21c4178.png"
path_colaborativo = Path("temas_sugeridos_colaborativos.json")

atividades_genericas = {
    "Promoção da equidade e inclusão": "Adaptação de recursos para alunos com necessidades específicas",
    "Estímulo à participação democrática": "Debate ou assembleia escolar simulada",
    "Desenvolvimento do pensamento crítico": "Análise de dilemas éticos contemporâneos",
    "Integração com problemas reais da sociedade": "Estudo de caso sobre questões locais",
    "Uso ético e consciente das tecnologias": "Discussão sobre privacidade e comportamento online",
    "Valorização de identidades e culturas diversas": "Feira cultural ou roda de saberes",
    "Empatia e diálogo": "Oficina de escuta ativa e expressão emocional",
    "Consciência socioambiental": "Projeto de reaproveitamento de materiais",
    "Direitos humanos e justiça social": "Análise de filmes ou reportagens sobre injustiças sociais",
    "Engajamento comunitário e responsabilidade coletiva": "Ações solidárias na comunidade local",
    "Cidadania digital": "Campanha educativa sobre cyberbullying e fake news"
}

criterios = list(atividades_genericas.keys())

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

# Título
st.title("Índice de Contribuição Cidadã (ICC)")

# Entrada de dados
nome = st.text_input("Seu nome:")
tema = st.text_input("Temática da pesquisa:")

pesos_usuario = {}
notas_usuario = {}

# Formulário principal
with st.form("icc_form"):
    for crit in criterios:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{crit}**")
        with col2:
            pesos_usuario[crit] = st.number_input("Peso", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key=f"peso_{crit}")
        with col3:
            notas_usuario[crit] = st.selectbox("Nota", [4, 3, 2, 1], key=f"nota_{crit}")
    submit = st.form_submit_button("Calcular ICC")

# Definir Session State para atividades marcadas
if "atividades_marcadas" not in st.session_state:
    st.session_state.atividades_marcadas = []

# Cálculo do ICC
if submit and nome and tema:
    icc = sum(converter_nota(notas_usuario[c]) * pesos_usuario[c] for c in criterios) / sum(pesos_usuario.values())
    st.success(f"ICC: {icc:.3f}")
    st.info(interpretar_icc(icc))

    st.markdown("### Gráfico de Desempenho por Critério")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[converter_nota(notas_usuario[c]) for c in criterios],
        theta=criterios,
        fill='toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
    st.plotly_chart(fig)

    # Radar para PDF
    radar_vals = [converter_nota(notas_usuario[c]) for c in criterios] + [converter_nota(notas_usuario[criterios[0]])]
    radar_labels = criterios + [criterios[0]]
    fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(radar_vals, linewidth=1)
    ax.fill(radar_vals, alpha=0.1)
    ax.set_xticks([i * 2 * 3.14159 / len(radar_labels) for i in range(len(radar_labels))])
    ax.set_xticklabels(radar_labels, fontsize=8)
    radar_path = "/tmp/grafico_icc_sessionstate.png"
    plt.savefig(radar_path)
    plt.close()

    st.markdown("### Sugestões de Atividades Relacionadas à Temática da Pesquisa que possam contribuir com o ICC")
    for i, (criterio, atividade) in enumerate(atividades_genericas.items()):
        if st.checkbox(f"{atividade}", key=f"check_{i}"):
            if atividade not in st.session_state.atividades_marcadas:
                st.session_state.atividades_marcadas.append(atividade)
        else:
            if atividade in st.session_state.atividades_marcadas:
                st.session_state.atividades_marcadas.remove(atividade)

    if st.button("Salvar atividades selecionadas"):
        if path_colaborativo.exists():
            with open(path_colaborativo, "r", encoding="utf-8") as f:
                base = json.load(f)
        else:
            base = {}
        base[tema.lower()] = st.session_state.atividades_marcadas
        with open(path_colaborativo, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=2, ensure_ascii=False)
        st.success(f"As seguintes atividades foram salvas para a temática '{tema}':\n- " + "\n- ".join(st.session_state.atividades_marcadas))

    # Geração do PDF
    pdf = RelatorioICC()
    pdf.add_page()
    pdf.chapter_title("Dados da Avaliação")
    pdf.chapter_body(f"Nome: {nome}\nTemática: {tema}\nICC: {icc:.3f}\n{interpretar_icc(icc)}")
    pdf.chapter_title("Notas e Pesos por Critério")
    for c in criterios:
        pdf.chapter_body(f"- {c}: Nota {notas_usuario[c]}, Peso {pesos_usuario[c]}")
    pdf.chapter_title("Gráfico Radar")
    pdf.image(radar_path, x=30, w=150)
    if st.session_state.atividades_marcadas:
        pdf.chapter_title("Atividades Curadas Selecionadas")
        for a in st.session_state.atividades_marcadas:
            pdf.chapter_body(f"- {a}")
    pdf_path = "/tmp/relatorio_icc_sessionstate.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Baixar Relatório PDF", f, file_name="relatorio_icc_sessionstate.pdf")