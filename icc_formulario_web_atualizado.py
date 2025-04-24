
import streamlit as st
import plotly.graph_objects as go

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

# Interpretação automática do ICC
def interpretar_icc(valor):
    if valor >= 0.85:
        return "Excelente contribuição para a formação cidadã e a diversidade social."
    elif valor >= 0.7:
        return "Boa contribuição, com potencial de fortalecimento em alguns critérios."
    elif valor >= 0.5:
        return "Contribuição regular, recomenda-se revisão e reforço em múltiplas dimensões."
    else:
        return "Baixa contribuição; é necessário reestruturar a proposta para ampliar o impacto cidadão."

# Cálculo e resultado
if submitted:
    numerador = 0
    denominador = 0
    notas_convertidas = {}

    for criterio, peso in criterios_pesos.items():
        nota_convertida = converter_nota(notas_usuario[criterio])
        notas_convertidas[criterio] = nota_convertida
        numerador += nota_convertida * peso
        denominador += peso

    icc = numerador / denominador

    st.success(f"Índice de Contribuição Cidadã (ICC): {icc:.3f}")
    st.info(interpretar_icc(icc))
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

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
