
import streamlit as st

# Título
st.title("Índice de Contribuição Cidadã (ICC)")
st.markdown("Preencha as notas (de 1 a 4) para cada critério da rubrica:")

# Critérios e pesos
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

# Conversão da nota para a escala [0, 1]
def converter_nota(nota):
    return {
        4: 1.0,
        3: 0.75,
        2: 0.5,
        1: 0.25
    }.get(nota, 0)

notas_usuario = {}
with st.form("form_icc"):
    for criterio in criterios_pesos:
        notas_usuario[criterio] = st.selectbox(
            criterio,
            options=[4, 3, 2, 1],
            format_func=lambda x: f"{x} - " + 
                {4: "Excelente", 3: "Bom", 2: "Regular", 1: "Insuficiente"}[x]
        )
    submitted = st.form_submit_button("Calcular ICC")

# Cálculo e resultado
if submitted:
    numerador = 0
    denominador = 0

    for criterio, peso in criterios_pesos.items():
        nota_convertida = converter_nota(notas_usuario[criterio])
        numerador += nota_convertida * peso
        denominador += peso

    icc = numerador / denominador
    st.success(f"Índice de Contribuição Cidadã (ICC): {icc:.3f}")
    st.progress(icc)
