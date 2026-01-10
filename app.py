import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF
import unicodedata

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E ESTADO DA SESSÃO
# =================================================================
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: CONEXÃO COM NOTION (ORDEM CORRETA)
# =================================================================
def carregar_dados_do_notion():
    NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
    DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados_notion = []
            for page in results:
                p = page.get("properties", {})
                dados_notion.append({
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            df = pd.DataFrame(dados_notion)
            # Ordenação numérica para garantir sequência 1, 2, 3...
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: INTERFACE E PDF PROFISSIONAL
# =================================================================
st.markdown("""<style>.stApp { background-color: #4169E1 !important; } h1, h2, h3, p, label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900 !important; border-radius: 10px !important; height: 3.5em; width: 100%; }</style>""", unsafe_allow_html=True)

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Zion Rancho App</h1>", unsafe_allow_html=True)
    if os.path.exists("APPRANCHO.png"): st.image("APPRANCHO.png", use_container_width=True)
    if st.button("INICIAR ACESSO"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso")
    navio_sel = st.selectbox("Embarcação", [""] + list(USUARIOS.keys()))
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        if navio_sel in USUARIOS and USUARIOS[navio_sel]["senha"] == senha:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()

elif st.session_state.pagina == "menu":
    st.title(f"Olá, {st.session_state.cozinheiro}!")
    if st.button("🛒 LISTA DE RANCHO"):
        st.session_state.pagina = "lista"
        st.rerun()
    if st.button("👨‍✈️ TRIPULAÇÃO"):
        st.session_state.pagina = "tripulacao"
        st.rerun()

elif st.session_state.pagina == "lista":
    st.title(f"📋 Rancho - {st.session_state.navio}")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.TextColumn("ITEM", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
            "UNID MED": st.column_config.TextColumn("UNID.", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("ESTOQUE", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA", min_value=0),
        },
        hide_index=True, use_container_width=True
    )

    st.markdown("---")
    
    # --- SUB-BLOCO DE GERAÇÃO DO PDF PROFISSIONAL ---
    if st.button("📄 GERAR PDF"):
        def blindar_texto(texto):
            return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')

        class PDF(FPDF):
            def header(self):
                if os.path.exists("APPRANCHO.png"): self.image("APPRANCHO.png", 10, 8, 20)
                self.set_font("Arial", "B", 14)
                self.set_xy(35, 12)
                self.cell(0, 10, blindar_texto(f"Checklist de Rancho - Responsavel: {st.session_state.cozinheiro}"), 0, 1)
                self.ln(10)
                # Cabeçalho Azul
                self.set_font("Arial", "B", 8)
                self.set_fill_color(0, 102, 204)
                self.set_text_color(255, 255, 255)
                self.cell(12, 10, "ITEM", 1, 0, "C", True)
                self.cell(70, 10, "DESCRICAO", 1, 0, "C", True)
                self.cell(45, 10, "TIPO", 1, 0, "C", True)
                self.cell(15, 10, "UNID", 1, 0, "C", True)
                self.cell(18, 10, "ESTOQUE", 1, 0, "C", True)
                self.cell(30, 10, "CONF.", 1, 1, "C", True)
                self.set_text_color(0, 0, 0)

        try:
            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=20)
            pdf.add_page()
            pdf.set_font("Arial", "", 8)

            for _, row in df_editado.iterrows():
                texto_desc = blindar_texto(row["DESCRIÇÃO"])
                texto_tipo = blindar_texto(row["TIPO"])
                alt_linha = 6
                linhas = max(int(pdf.get_string_width(texto_desc)/70)+1, int(pdf.get_string_width(texto_tipo)/45)+1)
                h = linhas * alt_linha
                
                if pdf.get_y() + h > 275: pdf.add_page()
                
                x, y = pdf.get_x(), pdf.get_y()
                pdf.cell(12, h, str(int(row["ITEM"])), 1, 0, "C")
                pdf.multi_cell(70, alt_linha, texto_desc, 1, "L")
                pdf.set_xy(x + 82, y)
                pdf.multi_cell(45, alt_linha, texto_tipo, 1, "C")
                pdf.set_xy(x + 127, y)
                pdf.cell(15, h, blindar_texto(row["UNID MED"]), 1, 0, "C")
                pdf.cell(18, h, str(row["PREDEFINIDO"]), 1, 0, "C")
                pdf.cell(30, h, str(row["CONFIRMA"]), 1, 1, "C")

            pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 BAIXAR PDF", data=pdf_output, file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Erro: {e}")

    # --- BOTÃO VOLTAR (RESTAURADO) ---
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Tripulação")
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"
        st.rerun()
