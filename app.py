import streamlit as st
import pandas as pd
import requests
import os
from fpdf import FPDF
import unicodedata

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E TRAVAS DE SEGURANÇA
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
# BLOCO 2: CONEXÃO COM NOTION (COM CORREÇÃO DE ORDEM)
# =================================================================
def carregar_dados_do_notion():
    # Suas chaves de acesso conforme imagem
    NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
    DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
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
            
            # --- PULO DO GATO PARA A SEQUÊNCIA ---
            # Converte a coluna ITEM para número para garantir a ordem 1, 2, 3... (e não 1, 10, 2)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            df = df.sort_values(by='ITEM').reset_index(drop=True)
            # -------------------------------------------------------------------------------
            
            return df
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO E TELA DE LISTA
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #4169E1 !important; }
    h1, h2, h3, p, label { color: white !important; }
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: black !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        height: 3.5em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Zion Rancho App</h1>", unsafe_allow_html=True)
    if os.path.exists("APPRANCHO.png"):
        st.image("APPRANCHO.png", use_container_width=True)
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
    
    # Botão de atualizar dados
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    if st.session_state.df_lista.empty:
        st.warning("⚠️ A lista está vazia. Clique no botão 'ATUALIZAR DADOS' acima.")
    else:
        # TRAVA: Apenas 'CONFIRMA' editável
        df_editado = st.data_editor(
            st.session_state.df_lista,
            column_config={
                "ITEM": st.column_config.TextColumn("ITEM", disabled=True),
                "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
                "TIPO": st.column_config.TextColumn("TIPO", disabled=True),
                "UNID MED": st.column_config.TextColumn("UNID.", disabled=True),
                "PREDEFINIDO": st.column_config.NumberColumn("PREDEF.", disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("CONFIRMA", min_value=0),
            },
            hide_index=True,
            use_container_width=True
        )

        st.markdown("---")
        
        # GERAÇÃO DO PDF (RETRATO + QUEBRA DE LINHA)
        if st.button("📄 GERAR PDF"):
            def blindar_texto(texto):
                return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')

            try:
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                # Título com o nome do responsável logado
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, blindar_texto(f"Checklist de Rancho - Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
                pdf.ln(5)
                
                # Cabeçalho da Tabela
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(200, 200, 200)
                larg_item, larg_desc, larg_tipo, larg_unid, larg_pre, larg_conf = 12, 78, 38, 17, 17, 28
                
                pdf.cell(larg_item, 10, "ITEM", 1, 0, "C", True)
                pdf.cell(larg_desc, 10, "DESCRICAO", 1, 0, "C", True)
                pdf.cell(larg_tipo, 10, "TIPO", 1, 0, "C", True)
                pdf.cell(larg_unid, 10, "UNID", 1, 0, "C", True)
                pdf.cell(larg_pre, 10, "ESTOQUE", 1, 0, "C", True)
                pdf.cell(larg_conf, 10, "CONF.", 1, 1, "C", True)

                pdf.set_font("Arial", "", 8)
                for _, row in df_editado.iterrows():
                    texto_desc = blindar_texto(row["DESCRIÇÃO"])
                    # Calcula altura dinâmica para respeitar os limites da célula
                    h = 8
                    x, y = pdf.get_x(), pdf.get_y()
                    
                    pdf.cell(larg_item, h, str(int(row["ITEM"])), 1, 0, "C")
                    pdf.multi_cell(larg_desc, h, texto_desc, 1, "L")
                    
                    final_y = pdf.get_y()
                    pdf.set_xy(x + larg_item + larg_desc, y)
                    dif_h = final_y - y
                    
                    pdf.cell(larg_tipo, dif_h, blindar_texto(row["TIPO"]), 1, 0, "C")
                    pdf.cell(larg_unid, dif_h, blindar_texto(row["UNID MED"]), 1, 0, "C")
                    pdf.cell(larg_pre, dif_h, str(row["PREDEFINIDO"]), 1, 0, "C")
                    pdf.cell(larg_conf, dif_h, str(row["CONFIRMA"]), 1, 1, "C")

                pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
                st.download_button("📥 BAIXAR PDF", data=pdf_output, file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"
        st.rerun()

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Tripulação")
    if st.button("⬅️ VOLTAR"):
        st.session_state.pagina = "menu"
        st.rerun()
