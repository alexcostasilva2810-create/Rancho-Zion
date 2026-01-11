import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
import pytz

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, IDs E ESTILOS GERAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Credenciais e IDs
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

# Inicialização de Variáveis de Estado
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame(columns=["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"])

# Funções Utilitárias
def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

def aplicar_estilo_tecnologico():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 20, 50, 0.88), rgba(0, 20, 50, 0.88)), 
            url('https://images.unsplash.com/photo-1544383333-546e16fd3a51?q=80&w=1920');
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; }
        .stButton > button {
            border: 1px solid #00D4FF !important; background: rgba(0, 212, 255, 0.1) !important;
            color: white !important; border-radius: 8px; width: 100%; height: 50px; font-weight: bold;
        }
        .stButton > button:hover { background: #00D4FF !important; color: black !important; }
        .mensagem-validade { 
            background-color: rgba(60, 45, 30, 0.9); 
            padding: 20px; border-radius: 8px; border-left: 6px solid #FF8C00;
            color: white; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 2: TELA HOME (ZION TECNOLOGIA)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #4169E1; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"): st.session_state.pagina = "login"; st.rerun()

# =================================================================
# BLOCO 3: TELA DE LOGIN
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio_sel = st.selectbox("Selecione a Embarcação", ["NAVIO 01", "AROEIRA", "NAVIO 03"])
    nome_user = st.text_input("Nome do Cozinheiro Responsável")
    if st.button("ENTRAR NO SISTEMA"):
        if nome_user:
            st.session_state.cozinheiro = nome_user
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.warning("Por favor, informe seu nome.")

# =================================================================
# BLOCO 4: MENU PRINCIPAL (PROFISSIONAL)
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_tecnologico()
    h1, h2 = st.columns([1, 6])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with h2: st.markdown(f"<h1>Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with c2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.button("⬅️ SAIR", use_container_width=True): st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 6: CONFERÊNCIA DE ESTOQUE (RESTAURADO E FUNCIONAL)
# =================================================================
elif st.session_state.pagina == "lista":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho com Logo e Título alinhados
    col_logo, col_tit = st.columns([1, 8])
    with col_logo:
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=70)
    with col_tit:
        st.markdown("<h2 style='color: white; margin-top: 10px;'>📋 Conferência de Estoque</h2>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Botão de Atualização com mapeamento direto das colunas do Notion
    if st.button("🔄 ATUALIZAR LISTA DO NOTION", use_container_width=True):
        headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
        try:
            response = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=headers)
            if response.status_code == 200:
                data = response.json()
                itens = []
                for page in data["results"]:
                    p = page["properties"]
                    # Captura direta e segura para evitar 'Sem Descrição'
                    try:
                        nome_item = p["DESCRIÇÃO"]["title"][0]["text"]["content"] if p["DESCRIÇÃO"]["title"] else "N/A"
                        itens.append({
                            "ITEM": p["ITEM"]["number"] if p["ITEM"]["number"] else 0,
                            "DESCRIÇÃO": nome_item,
                            "TIPO": p["TIPO"]["select"]["name"] if p["TIPO"]["select"] else "DIVERSOS",
                            "UNID MED": p["UNID MED"]["select"]["name"] if p["UNID MED"]["select"] else "un",
                            "CONFIRMA": 0  # Coluna para o cozinheiro preencher
                        })
                    except Exception: continue
                
                st.session_state.df_lista = pd.DataFrame(itens).sort_values(by="ITEM")
                st.success("✅ Tabela atualizada com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")

    # Editor de Dados (Captura o que foi digitado)
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("CÓD.", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA", min_value=0)
        },
        hide_index=True, use_container_width=True, key="editor_estoque_fix"
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 GERAR E SALVAR RELATÓRIO"):
            fuso_br = pytz.timezone('America/Sao_Paulo')
            data_hora = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M:%S')
            
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
            pdf.set_font("Arial", "B", 14); pdf.set_y(35)
            pdf.cell(0, 10, preparar(f"Relatório de Rancho: {st.session_state.navio}"), ln=True, align="C")
            pdf.set_font("Arial", "", 10); pdf.cell(0, 8, preparar(f"Responsável: {st.session_state.cozinheiro} | Data: {data_hora}"), ln=True, align="C")
            pdf.ln(5)

            # Cabeçalho da Tabela no PDF
            pdf.set_fill_color(200, 220, 255); pdf.set_font("Arial", "B", 8)
            pdf.cell(15, 8, "COD", 1, 0, "C", True); pdf.cell(110, 8, "DESCRICAO", 1, 0, "L", True); pdf.cell(30, 8, "CONFIRMA", 1, 1, "C", True)
            
            # Dados - Usa df_editado para garantir que o PDF tenha conteúdo
            pdf.set_font("Arial", "", 8)
            for _, row in df_editado.iterrows():
                pdf.cell(15, 7, str(row["ITEM"]), 1, 0, "C")
                pdf.cell(110, 7, preparar(str(row["DESCRIÇÃO"])), 1, 0, "L")
                pdf.cell(30, 7, str(row["CONFIRMA"]), 1, 1, "C")
            
            st.download_button("📥 BAIXAR RELATÓRIO PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="Relatorio_Rancho.pdf")

    with c2:
        if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: DECLARAÇÃO (RESTAURADA COM DATAS BR)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    col_logo, col_tit = st.columns([1, 8])
    with col_logo:
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=70)
    with col_tit:
        st.markdown("<h2 style='color: white; margin-top: 10px;'>⚓ Declaração de Reabastecimento</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Responsável", value=st.session_state.cozinheiro, disabled=True)
        # Formato de data restaurado para DD/MM/YYYY
        data_ultimo = st.date_input("Data do Último Rancho", format="DD/MM/YYYY")
        origem = st.text_input("Origem", value="Porto Velho")
    with c2:
        data_pedido = st.date_input("Data do Pedido", value=datetime.now(), format="DD/MM/YYYY")
        escolta = st.selectbox("Possui Escolta?", ["NÃO", "SIM"])
        destino = st.text_input("Destino", value="Novo remanso")

    qtd_tripulantes = st.number_input("Tripulantes a bordo", min_value=1, value=14)
    dias = 12 if escolta == "SIM" else 15
    vencimento = data_pedido + timedelta(days=dias)
    
    st.markdown(f"""<div class='mensagem-validade'>📢 Duração: {dias} dias | Validade até: {vencimento.strftime('%d/%m/%Y')}</div>""", unsafe_allow_html=True)

    st.markdown("### ✍️ Assinatura do Comandante")
    canvas_result = st_canvas(fill_color="white", stroke_width=2, stroke_color="black", background_color="white", height=150, key="canvas_restored")
    consideracoes = st.text_area("CONSIDERAÇÕES:", placeholder="Observações adicionais...")

    st.markdown("---")
    if st.button("📄 GERAR PDF DA DECLARAÇÃO", use_container_width=True):
        if canvas_result.image_data is not None:
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 25)
            pdf.set_font("Arial", "B", 14); pdf.set_y(45)
            pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
            
            # Texto formal conforme imagem
            pdf.set_font("Arial", "", 11); pdf.ln(10)
            texto = (f"Pelo presente, certifico que a lotacao de tripulantes a bordo do empurrador e de {qtd_tripulantes} tripulantes. "
                     f"A provisao de rancho se destina a cobrir as necessidades por {dias} dias a partir de {data_pedido.strftime('%d/%m/%Y')}.")
            pdf.multi_cell(0, 8, preparar(texto))
            
            # Rodapé e Assinatura
            img_path = "temp_sig.png"
            Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').save(img_path)
            pdf.image(img_path, x=75, y=pdf.get_y() + 10, w=50)
            
            st.download_button("📥 BAIXAR DECLARAÇÃO", data=pdf.output(dest='S').encode('latin-1'), file_name="Declaracao.pdf")

    if st.button("⬅️ VOLTAR AO MENU", use_container_width=True):
        st.session_state.pagina = "menu"; st.rerun()
# =================================================================
# BLOCO 8: TELA DE HISTÓRICO
# =================================================================
elif st.session_state.pagina == "historico":
    aplicar_estilo_tecnologico()
    st.title("📜 Histórico de Registros")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
