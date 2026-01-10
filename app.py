import streamlit as st
import os

# 1. Configuração da Página
st.set_page_config(page_title="Zion Rancho", layout="centered")

# 2. Estilo Azul Royal
st.markdown("""
    <style>
    .stApp {
        background-color: #4169E1;
        color: white;
        text-align: center;
    }
    h1, p { color: white !important; }
    .stButton>button {
        background-color: white;
        color: #4169E1;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 50%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Conteúdo da Tela Inicial
st.title("Bem-vindo ao Zion Rancho App!")
st.write("Seu controle de estoque inteligente com IA.")

# Tentativa de carregar a imagem sem quebrar o app
nome_da_imagem = "robo_humanizado.jpg"

if os.path.exists(nome_da_imagem):
    st.image(nome_da_imagem, width=400)
else:
    st.error(f"Arquivo '{nome_da_imagem}' não encontrado no GitHub. Verifique o nome!")

# 4. Botão de entrada
if st.button("ACESSAR SISTEMA"):
    st.success("Conectando ao banco de dados...")
    # Aqui depois colocaremos a troca para a tabela
