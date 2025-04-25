import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import os
import matplotlib.pyplot as plt

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

st.markdown("### Avalie os critérios e defina os pesos correspondentes")

pesos_usuario = {}
notas_usuario = {}

with st.form("form_avaliacao"):
    for crit in criterios:
        cols = st.columns([2, 1, 1])
        with cols[0]:
            st.markdown(f"**{crit}**")
        with cols[1]:
            pesos_usuario[crit] = st.number_input(f"Peso", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key=f"peso_{crit}")
        with cols[2]:
            notas_usuario[crit] = st.selectbox("Nota", options=[4, 3, 2, 1], key=f"nota_{crit}")
    submitted = st.form_submit_button("Calcular ICC")

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


if submitted and nome and tema:
    st.markdown("### Sugestões de Atividades Relacionadas à Temática da Pesquisa que possam contribuir com o ICC")

    from difflib import get_close_matches
    tematicas_atividades = {
        "educação sexual": [
            "Rodas de conversa sobre identidade de gênero e sexualidade",
            "Cartazes educativos sobre respeito e prevenção",
            "Estudo de casos de bullying por orientação sexual"
        ],
        "meio ambiente": [
            "Projetos de horta escolar",
            "Campanhas de reciclagem",
            "Debates sobre mudanças climáticas"
        ],
        "violência escolar": [
            "Oficinas de resolução de conflitos",
            "Dramatizações sobre empatia",
            "Espaços de escuta ativa"
        ],
        "cidadania digital": [
            "Campanhas sobre cyberbullying",
            "Leitura crítica de redes sociais",
            "Conteúdo educativo sobre ética online"
        ],
        "diversidade cultural": [
            "Feiras multiculturais",
            "Murais sobre diversidade",
            "Vídeos sobre identidades culturais"
        ],
        "direitos humanos": [
            "Debates sobre desigualdades",
            "Casos de violações de direitos",
            "Textos sobre justiça social"
        ],
        "inclusão": [
            "Materiais acessíveis",
            "Jogos adaptados",
            "Mentorias com foco em deficiência"
        ]
    }

    def analisar_sugestoes_tema_livre(texto_usuario, base, cutoff=0.3):
        texto = texto_usuario.lower()
        palavras_tema = texto.split()
        matches = set()
        for palavra in palavras_tema:
            aproximados = get_close_matches(palavra, base.keys(), n=2, cutoff=cutoff)
            matches.update(aproximados)
        resultados = []
        for tema in matches:
            atividades = base.get(tema, [])
            resultados.extend([(tema, a) for a in atividades])
        return resultados

    sugestoes_semanticas = analisar_sugestoes_tema_livre(tema, tematicas_atividades, cutoff=0.3)
    if sugestoes_semanticas:
        df_sugestoes = pd.DataFrame(sugestoes_semanticas, columns=["Temática aproximada", "Atividade sugerida"])
        
    # Calcular impacto estimado e exibir ranking
    impacto_base = {
        "Rodas de conversa sobre identidade de gênero e sexualidade": 0.9,
        "Cartazes educativos sobre respeito e prevenção": 0.8,
        "Estudo de casos de bullying por orientação sexual": 0.85,
        "Projetos de horta escolar": 0.75,
        "Campanhas de reciclagem": 0.65,
        "Debates sobre mudanças climáticas": 0.7,
        "Oficinas de resolução de conflitos": 0.9,
        "Dramatizações sobre empatia": 0.8,
        "Espaços de escuta ativa": 0.85,
        "Campanhas sobre cyberbullying": 0.7,
        "Leitura crítica de redes sociais": 0.6,
        "Conteúdo educativo sobre ética online": 0.65,
        "Feiras multiculturais": 0.8,
        "Murais sobre diversidade": 0.75,
        "Vídeos sobre identidades culturais": 0.85,
        "Debates sobre desigualdades": 0.85,
        "Casos de violações de direitos": 0.8,
        "Textos sobre justiça social": 0.7,
        "Materiais acessíveis": 0.9,
        "Jogos adaptados": 0.8,
        "Mentorias com foco em deficiência": 0.9
    }

    sugestoes_rankeadas = [
        (tema, atividade, impacto_base.get(atividade, 0.5))
        for tema, atividade in sugestoes_semanticas
    ]
    df_ranking = pd.DataFrame(sugestoes_rankeadas, columns=["Temática aproximada", "Atividade sugerida", "Impacto estimado"])
    df_ranking = df_ranking.sort_values(by="Impacto estimado", ascending=False)
    st.dataframe(df_ranking)
    
    else:
        st.warning("Nenhuma sugestão automática foi encontrada com base na temática digitada.")

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

    st.markdown("### Resumo da Avaliação")
    df_result = pd.DataFrame({
        "Critério": criterios,
        "Peso": [pesos_usuario[c] for c in criterios],
        "Nota": [notas_usuario[c] for c in criterios],
        "Nota convertida": [notas_convertidas[c] for c in criterios]
    })
    st.dataframe(df_result)

    st.markdown("### Visualização por Critério")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(notas_convertidas.values()),
        theta=criterios,
        fill='toself',
        name='Desempenho'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico para PDF
    radar_vals = list(notas_convertidas.values()) + [list(notas_convertidas.values())[0]]
    radar_labels = criterios + [criterios[0]]
    fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(radar_vals, linewidth=1, linestyle='solid')
    ax.fill(radar_vals, 'b', alpha=0.1)
    ax.set_xticks([i * 2 * 3.14159 / len(radar_labels) for i in range(len(radar_labels))])
    ax.set_xticklabels(radar_labels, fontsize=8)
    radar_path = "/tmp/icc_grafico_radar_tabela.png"
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
    
    pdf.chapter_title("Sugestões de Atividades por Temática Aproximada")
    for tema, atividade, impacto in sugestoes_rankeadas:
        pdf.chapter_body(f"{tema} - {atividade} (Impacto estimado: {impacto})")
    pdf_path = "/tmp/relatorio_icc_tabela.pdf"
    
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Baixar Relatório PDF com Avaliação", f, file_name="relatorio_icc_tabela.pdf")