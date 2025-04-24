import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
from difflib import get_close_matches
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

# Atividades extraídas automaticamente do .docx
atividades_por_criterio = {
    "Promoção da equidade e inclusão": [
        "Adaptação de materiais didáticos para diferentes necessidades",
        "Uso de linguagem inclusiva nas comunicações escolares",
        "Formação de professores sobre práticas antidiscriminatórias",
        "Promoção de campanhas de valorização da diversidade",
        "Aplicação de avaliações com critérios inclusivos",
        "Implementação de tutoria entre pares",
        "Criação de grupos de apoio a estudantes com deficiência",
        "Mapeamento da diversidade identitária",
        "Uso de tecnologias assistivas em sala",
        "Ações afirmativas para grupos minorizados"
    ],
    "Consciência socioambiental": [
        "Projetos de reciclagem e reaproveitamento",
        "Campanhas de conscientização ambiental",
        "Hortas escolares sustentáveis",
        "Oficinas sobre consumo consciente",
        "Visitas a reservas ambientais",
        "Debates sobre mudanças climáticas",
        "Feiras ecológicas",
        "Criação de produtos ecológicos",
        "Atividades sobre economia circular",
        "Análise de documentários sobre meio ambiente"
    ],
    "Cidadania digital": [
        "Aulas sobre direitos e deveres digitais",
        "Discussão sobre cyberbullying e discurso de ódio",
        "Campanhas de uso consciente da internet",
        "Criação de conteúdo educativo digital",
        "Análise de algoritmos e bolhas de filtro",
        "Estudo crítico de termos de uso e privacidade",
        "Gamificação cidadã",
        "Produção de podcasts sobre ética online",
        "Criação de infográficos digitais",
        "Simulações jurídicas online"
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

    # Gráfico de radar
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

    # Sugestão baseada na temática
    st.markdown("### Sugestões de Atividades Relacionadas à Temática da Pesquisa")
    sugestoes = []
    for criterio, atividades in atividades_por_criterio.items():
        if any(palavra in criterio.lower() or palavra in tema.lower()
               for palavra in tema.lower().split()):
            for atividade in atividades:
                sugestoes.append((criterio, atividade))

    if sugestoes:
        df_sugestoes = pd.DataFrame(sugestoes, columns=["Critério", "Atividade"])
        st.dataframe(df_sugestoes)
    else:
        st.warning("Não foram encontradas sugestões diretas com base na temática. Tente usar palavras-chave mais claras.")