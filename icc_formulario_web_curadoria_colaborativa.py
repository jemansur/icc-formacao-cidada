import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path

logo_path = "c84616cb-25bb-448d-9739-31c9e21c4178.png"
path_base_colaborativa = Path("temas_sugeridos_colaborativos.json")

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

atividades_sugeridas_genericas = {
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

# Interface
st.title("ICC com Curadoria Colaborativa de Atividades")
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
    numerador = sum(converter_nota(notas_usuario[c]) * pesos_usuario[c] for c in criterios)
    denominador = sum(pesos_usuario[c] for c in criterios)
    icc = numerador / denominador
    st.success(f"ICC: {icc:.3f}")
    st.info(interpretar_icc(icc))

    # Curadoria de sugestões
    sugestoes_curadas = []
    st.markdown("### Sugestões de Atividades para Nova Temática")
    st.markdown("Marque as atividades que podem ser associadas à temática digitada.")
    for crit, atividade in atividades_sugeridas_genericas.items():
        if st.checkbox(atividade):
            sugestoes_curadas.append(atividade)

    if sugestoes_curadas and st.button("Salvar temática e atividades selecionadas"):
        if path_base_colaborativa.exists():
            with open(path_base_colaborativa, "r", encoding="utf-8") as f:
                base = json.load(f)
        else:
            base = {}

        tema_key = tema.strip().lower()
        base[tema_key] = sugestoes_curadas
        with open(path_base_colaborativa, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=2, ensure_ascii=False)
        st.success(f"Temática '{tema}' salva com {len(sugestoes_curadas)} atividade(s) marcadas.")