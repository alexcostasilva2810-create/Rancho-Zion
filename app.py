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
        
       # GERAÇÃO DO PDF (RETRATO + AJUSTE DE COLUNAS + LOGO NO RODAPÉ)
        if st.button("📄 GERAR PDF"):
            def blindar_texto(texto):
                return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')

            try:
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.set_auto_page_break(auto=True, margin=25) # Margem maior para a logo
                pdf.add_page()
                
                # Cabeçalho
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, blindar_texto(f"Checklist de Rancho - Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
                pdf.ln(5)
                
                # Configuração de Larguras (Total 190mm)
                # Ajustei o TIPO para 40mm para caber melhor o texto longo
                larg_item, larg_desc, larg_tipo, larg_unid, larg_pre, larg_conf = 12, 75, 40, 15, 18, 30
                
                pdf.set_font("Arial", "B", 8)
                pdf.set_fill_color(200, 200, 200)
                pdf.cell(larg_item, 10, "ITEM", 1, 0, "C", True)
                pdf.cell(larg_desc, 10, "DESCRICAO", 1, 0, "C", True)
                pdf.cell(larg_tipo, 10, "TIPO", 1, 0, "C", True)
                pdf.cell(larg_unid, 10, "UNID", 1, 0, "C", True)
                pdf.cell(larg_pre, 10, "ESTOQUE", 1, 0, "C", True)
                pdf.cell(larg_conf, 10, "CONF.", 1, 1, "C", True)

                pdf.set_font("Arial", "", 8)
                
                for _, row in df_editado.iterrows():
                    # PULO DO GATO: Cálculo de altura para múltiplas células na mesma linha
                    # Verificamos qual texto é mais longo para definir a altura da borda
                    texto_desc = blindar_texto(row["DESCRIÇÃO"])
                    texto_tipo = blindar_texto(row["TIPO"])
                    
                    x_inicial = pdf.get_x()
                    y_inicial = pdf.get_y()
                    
                    # 1. Coluna Item
                    pdf.cell(larg_item, 10, str(int(row["ITEM"])), 1, 0, "C")
                    
                    # 2. Coluna Descrição (com quebra)
                    pdf.multi_cell(larg_desc, 5, texto_desc, 1, "L")
                    y_apos_desc = pdf.get_y()
                    
                    # Volta para o lado da descrição para fazer o Tipo
                    pdf.set_xy(x_inicial + larg_item + larg_desc, y_inicial)
                    
                    # 3. Coluna Tipo (Ajustada para quebrar e não vazar)
                    pdf.multi_cell(larg_tipo, 5, texto_tipo, 1, "C")
                    y_apos_tipo = pdf.get_y()
                    
                    # Define a maior altura atingida nesta linha para alinhar as próximas colunas
                    altura_max = max(y_apos_desc, y_apos_tipo)
                    dif_h = altura_max - y_inicial
                    
                    # Ajusta a posição para as colunas finais
                    pdf.set_xy(x_inicial + larg_item + larg_desc + larg_tipo, y_inicial)
                    
                    # 4. Colunas Restantes (ajustando a moldura pela altura_max)
                    pdf.cell(larg_unid, dif_h, blindar_texto(row["UNID MED"]), 1, 0, "C")
                    pdf.cell(larg_pre, dif_h, str(row["PREDEFINIDO"]), 1, 0, "C")
                    pdf.cell(larg_conf, dif_h, str(row["CONFIRMA"]), 1, 1, "C")

                    # MARCA D'ÁGUA / LOGO NO CANTO INFERIOR ESQUERDO
                    # Posiciona a 15mm do fim da página (área branca)
                    if os.path.exists("APPRANCHO.png"):
                        pdf.image("APPRANCHO.png", x=10, y=270, w=30) 

                pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
                st.download_button("📥 BAIXAR PDF", data=pdf_output, file_name=f"Rancho_{st.session_state.navio}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro no ajuste de tabela: {e}")
