import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import json
from difflib import get_close_matches
from pathlib import Path

logo_path = "c84616cb-25bb-448d-9739-31c9e21c4178.png"
path_temas = Path("temas_sugeridos.json")

# Base inicial
tematicas_atividades = {
    "educação sexual": [
        "Rodas de conversa sobre identidade de gênero e sexualidade",
        "Cartazes educativos sobre respeito e prevenção"
    ],
    "meio ambiente": [
        "Projetos de horta escolar",
        "Campanhas de reciclagem"
    ]
}

# Carregar temáticas salvas
if path_temas.exists():
    with open(path_temas, "r", encoding="utf-8") as f:
        tematicas_atividades.update(json.load(f))

def salvar_nova_tematica(tema_novo, atividades_sugeridas):
    if path_temas.exists():
        with open(path_temas, "r", encoding="utf-8") as f:
            base = json.load(f)
    else:
        base = {}
    tema_key = tema_novo.strip().lower()
    if tema_key not in base:
        base[tema_key] = atividades_sugeridas
        with open(path_temas, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=2, ensure_ascii=False)

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

impacto_base = {atividade: 0.75 for lista in tematicas_atividades.values() for atividade in lista}

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

st.title("ICC - Índice de Contribuição Cidadã (Autoaprendizagem)")

nome = st.text_input("Seu nome:")
tema = st.text_input("Temática da pesquisa:")

pesos_usuario = {}
notas_usuario = {}

with st.form("formulario_icc"):
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

    # Sugestões inteligentes
    palavras = tema.lower().split()
    matches = set()
    for p in palavras:
        similares = get_close_matches(p, tematicas_atividades.keys(), n=1, cutoff=0.3)
        matches.update(similares)

    sugestoes = []
    for match in matches:
        for a in tematicas_atividades[match]:
            sugestoes.append((match, a, impacto_base.get(a, 0.5)))

    st.markdown("### Sugestões Inteligentes por Temática Aproximada")
    if sugestoes:
        df = pd.DataFrame(sugestoes, columns=["Temática", "Atividade sugerida", "Impacto estimado"])
        df = df.sort_values(by="Impacto estimado", ascending=False)
        st.dataframe(df)
    else:
        st.warning("Nenhuma correspondência direta. Deseja sugerir atividades para esta nova temática?")
        atividades_txt = st.text_area("Liste atividades (uma por linha):")
        if atividades_txt and st.button("Salvar nova temática"):
            lista_atividades = [a.strip() for a in atividades_txt.strip().split("\n") if a.strip()]
            salvar_nova_tematica(tema, lista_atividades)
            st.success("Temática registrada com sucesso! Obrigado por contribuir. 🚀")