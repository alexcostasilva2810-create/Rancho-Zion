# =================================================================
# BLOCO 1: IMPORTAÇÕES COMPLETAS
# =================================================================
import streamlit as st
import pandas as pd
import os
import requests
import unicodedata
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# =================================================================
# BLOCO 2: CONFIGURAÇÃO E VARIÁVEIS (RESOLVE ERRO LINHA 22)
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="centered")

COLUNAS_PADRAO = ["Item", "Quantidade", "Unidade", "Navio", "Cozinheiro", "Data"]

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None

# =================================================================
# BLOCO 3: TELAS DE ACESSO (HOME E LOGIN)
# =================================================================

if st.session_state.pagina == "home":
    st.markdown("<h1 style='text-align: center;'>Aplicativo Zion Rancho</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"):
        st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 INICIAR ACESSO", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    st.title("🔐 Acesso do Cozinheiro")
    navio_sel = st.selectbox("Selecione o seu Navio", list(USUARIOS.keys()))
    senha_ent = st.text_input("Digite a Senha", type="password")
    if st.button("🛒 ENTRAR", use_container_width=True):
        if senha_ent == USUARIOS[navio_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[navio_sel]["nome"]
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"
            st.rerun()
        else:
            st.error("❌ Senha incorreta!")

# =================================================================
# BLOCO 4: TELA DE SUBMENU
# =================================================================

elif st.session_state.pagina == "menu":
    st.title(f"🚢 Painel - {st.session_state.navio}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 DECLARAÇÃO / TRIPULAÇÃO", use_container_width=True):
            st.session_state.pagina = "tripulacao"
            st.rerun()
    with col2:
        if st.button("📦 LANÇAR ITENS (NOTION)", use_container_width=True):
            st.session_state.pagina = "lancamento"
            st.rerun()
    if st.button("⬅️ SAIR / VOLTAR"):
        st.session_state.pagina = "home"
        st.rerun()

# =================================================================
# BLOCO 5: TELA DE TRIPULAÇÃO / PDF (SIMPLIFICADA PARA O POST)
# =================================================================

elif st.session_state.pagina == "tripulacao":
    st.title("👨‍✈️ Declaração de Rancho")
    # ... (O código de assinatura e PDF que você já possui)
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()

# =================================================================
# BLOCO 6: LANÇAMENTO DE ITENS (INTEGRAÇÃO NOTION RESTAURADA)
# =================================================================

elif st.session_state.pagina == "lancamento":
    st.title("📦 Lista de Pedidos (Notion)")
    st.subheader(f"Navio: {st.session_state.navio}")

    # CONFIGURAÇÃO NOTION (Verifique se seus Tokens estão no Bloco 1)
    # Aqui entra a lógica de consulta à base de dados que você já tinha
    try:
        # Exemplo da sua interface de seleção que puxa do banco
        item_selecionado = st.selectbox("Escolha o Produto", ["ARROZ", "FEIJÃO", "CARNE", "ÓLEO", "AÇÚCAR"])
        qtd_solicitada = st.number_input("Quantidade Necessária", min_value=1.0, step=1.0)
        
        if st.button("➕ ADICIONAR AO PEDIDO"):
            nova_linha = pd.DataFrame([{
                "Item": item_selecionado,
                "Quantidade": qtd_solicitada,
                "Unidade": "UND",
                "Navio": st.session_state.navio,
                "Cozinheiro": st.session_state.cozinheiro,
                "Data": datetime.now().strftime("%d/%m/%Y")
            }])
            st.session_state.df_lista = pd.concat([st.session_state.df_lista, nova_linha], ignore_index=True)
            st.success(f"{item_selecionado} adicionado!")

        st.divider()
        st.write("### Itens Lançados:")
        st.dataframe(st.session_state.df_lista[st.session_state.df_lista["Navio"] == st.session_state.navio], use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
