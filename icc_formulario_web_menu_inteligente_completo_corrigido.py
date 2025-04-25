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

# Banco semântico inicial
banco_semantico = {
    "educação antirracista": {
        "keywords": ["racismo", "etnia", "afro", "discriminação", "negritude"],
        "atividades": [
            "Roda de conversa sobre identidade racial",
            "Produção de murais sobre igualdade étnico-racial",
            "Análise de livros com protagonistas negros"
        ]
    },
    "inclusão e acessibilidade": {
        "keywords": ["inclusão", "acessível", "deficiência", "libras", "diversidade funcional"],
        "atividades": [
            "Produção de materiais acessíveis",
            "Oficinas de sensibilização sobre deficiência",
            "Palestras sobre educação inclusiva"
        ]
    },
    "direitos humanos": {
        "keywords": ["direitos", "igualdade", "justiça social", "direitos civis"],
        "atividades": [
            "Análise de casos de violações de direitos",
            "Campanhas de conscientização sobre direitos humanos",
            "Simulações de tribunal de direitos humanos"
        ]
    },
}

# Carregar banco salvo
if path_colaborativo.exists():
    with open(path_colaborativo, "r", encoding="utf-8") as f:
        banco_salvo = json.load(f)
    banco_semantico.update(banco_salvo)

def salvar_banco():
    with open(path_colaborativo, "w", encoding="utf-8") as f:
        json.dump(banco_semantico, f, indent=2, ensure_ascii=False)

def encontrar_atividades(tema_digitado):
    tema_digitado = tema_digitado.lower()
    atividades = []
    for tema, dados in banco_semantico.items():
        if any(palavra in tema_digitado for palavra in dados["keywords"]) or tema in tema_digitado:
            atividades.extend(dados["atividades"])
    return atividades

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

# Menu inicial
st.title("Índice de Contribuição Cidadã (ICC)")

opcao = st.radio("O que você deseja fazer?", ["Preencher ICC", "Alimentar Banco de Temáticas e Atividades"])

if opcao == "Preencher ICC":
    if "atividades_marcadas" not in st.session_state:
        st.session_state.atividades_marcadas = []

    if "icc_calculado" not in st.session_state:
        st.session_state.icc_calculado = False

    nome = st.text_input("Seu nome:")
    tema = st.text_input("Temática da pesquisa:")

    pesos_usuario = {}
    notas_usuario = {}

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

    with st.form("formulario_icc"):
        for crit in criterios:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{crit}**")
            with col2:
                pesos_usuario[crit] = st.number_input(f"Peso", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key=f"peso_{crit}")
            with col3:
                notas_usuario[crit] = st.selectbox("Nota", [4, 3, 2, 1], key=f"nota_{crit}")
        calcular = st.form_submit_button("Calcular ICC")

    if calcular:
        icc = sum(converter_nota(notas_usuario[c]) * pesos_usuario[c] for c in criterios) / sum(pesos_usuario.values())
        st.session_state.icc_valor = icc
        st.session_state.notas = notas_usuario
        st.session_state.pesos = pesos_usuario
        st.session_state.nome = nome
        st.session_state.tema = tema
        st.session_state.icc_calculado = True

    if st.session_state.icc_calculado:
        st.success(f"ICC: {st.session_state.icc_valor:.3f}")
        st.info(interpretar_icc(st.session_state.icc_valor))

        st.subheader("📈 Gráfico de Desempenho por Critério")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[converter_nota(st.session_state.notas[c]) for c in criterios],
            theta=criterios,
            fill='toself'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
        st.plotly_chart(fig)

        radar_vals = [converter_nota(st.session_state.notas[c]) for c in criterios] + [converter_nota(st.session_state.notas[criterios[0]])]
        radar_labels = criterios + [criterios[0]]
        fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(radar_vals, linewidth=1)
        ax.fill(radar_vals, alpha=0.1)
        ax.set_xticks([i * 2 * 3.14159 / len(radar_labels) for i in range(len(radar_labels))])
        ax.set_xticklabels(radar_labels, fontsize=8)
        radar_path = "/tmp/grafico_icc_inteligente.png"
        plt.savefig(radar_path)
        plt.close()

        atividades_sugeridas = encontrar_atividades(st.session_state.tema)

        st.subheader("✅ Sugestões de Atividades Relacionadas")
        if atividades_sugeridas:
            for atividade in atividades_sugeridas:
                if st.checkbox(atividade, key=f"sugerida_{atividade}"):
                    if atividade not in st.session_state.atividades_marcadas:
                        st.session_state.atividades_marcadas.append(atividade)
                else:
                    if atividade in st.session_state.atividades_marcadas:
                        st.session_state.atividades_marcadas.remove(atividade)
        else:
            st.info("Nenhuma sugestão encontrada. Contribua sugerindo novas atividades!")

        novas_sugestoes = st.text_area("📝 Deseja sugerir outras atividades? (separadas por linha)", key="sugestoes_livres")

        if st.button("Salvar atividades sugeridas", key="salvar_marcadas_e_livres_icc"):
            todas_atividades = st.session_state.atividades_marcadas.copy()
            if novas_sugestoes.strip():
                novas = [a.strip() for a in novas_sugestoes.strip().split("\n") if a.strip()]
                todas_atividades.extend(novas)

            if st.session_state.tema.lower() not in banco_semantico:
                banco_semantico[st.session_state.tema.lower()] = {
                    "keywords": [],
                    "atividades": todas_atividades
                }
            else:
                banco_semantico[st.session_state.tema.lower()]["atividades"].extend(todas_atividades)

            salvar_banco()
            st.success(f"Atividades salvas para a temática '{st.session_state.tema}'.")

        
todas_atividades = st.session_state.atividades_marcadas.copy()
if novas_sugestoes.strip():
    novas = [a.strip() for a in novas_sugestoes.strip().split("\n") if a.strip()]
    todas_atividades.extend(novas)

pdf = RelatorioICC()

        pdf.add_page()
        pdf.chapter_title("Dados da Avaliação")
        pdf.chapter_body(f"Nome: {st.session_state.nome}\nTemática: {st.session_state.tema}\nICC: {st.session_state.icc_valor:.3f}\n{interpretar_icc(st.session_state.icc_valor)}")
        pdf.chapter_title("Notas e Pesos por Critério")
        for c in criterios:
            pdf.chapter_body(f"- {c}: Nota {st.session_state.notas[c]}, Peso {st.session_state.pesos[c]}")
        pdf.chapter_title("Gráfico Radar")
        pdf.image(radar_path, x=30, w=150)
        if todas_atividades:
            pdf.chapter_title("Atividades Curadas e Sugeridas")
            for a in todas_atividades:
                pdf.chapter_body(f"- {a}")
        pdf_path = "/tmp/relatorio_icc_final.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Baixar Relatório PDF", f, file_name="relatorio_icc_final.pdf")

else:
    st.subheader("🛠 Alimentar Banco de Temáticas e Atividades")

    nova_tematica = st.text_input("Nova Temática:")
    novas_palavras = st.text_input("Palavras-chave associadas (separadas por vírgula):")
    novas_atividades = st.text_area("Atividades relacionadas (uma por linha):")

    if st.button("Adicionar ao Banco Semântico", key="adicionar_banco_semantico"):
        if nova_tematica and novas_palavras and novas_atividades:
            palavras = [p.strip().lower() for p in novas_palavras.split(",") if p.strip()]
            atividades = [a.strip() for a in novas_atividades.strip().split("\n") if a.strip()]
            banco_semantico[nova_tematica.lower()] = {
                "keywords": palavras,
                "atividades": atividades
            }
            salvar_banco()
            st.success(f"Nova temática '{nova_tematica}' adicionada com sucesso!")

    if st.button("📋 Ver Banco de Temáticas Existentes", key="listar_banco_existente"):
        dados = []
        for tema, conteudo in banco_semantico.items():
            dados.append({
                "Temática": tema.title(),
                "Palavras-chave": ", ".join(conteudo.get("keywords", [])),
                "Atividades": "; ".join(conteudo.get("atividades", []))
            })
        df_banco = pd.DataFrame(dados)
        st.dataframe(df_banco)