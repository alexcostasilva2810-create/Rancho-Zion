import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E IDs
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame()

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"},
    "ADMIN": {"nome": "Administrador", "senha": "zion"}
}

def preparar_celula(conteudo):
    texto = str(conteudo) if conteudo is not None else ""
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

# =================================================================
# BLOCO 2: TELAS
# =================================================================

# --- HOME ---
if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #FF8C00; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: black;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA", key="btn_h"): st.session_state.pagina = "login"; st.rerun()

# --- LOGIN (FUNDO LARANJA / LETRA PRETA) ---
elif st.session_state.pagina == "login":
    st.markdown("""<style>
        .stApp { background-color: #FF8C00; }
        h1, label, p { color: black !important; font-weight: bold; }
        input { color: black !important; }
    </style>""", unsafe_allow_html=True)
    st.title("🔐 Login")
    n_sel = st.selectbox("Selecione o Navio", list(USUARIOS.keys()), key="l1")
    s_dig = st.text_input("Senha", type="password", key="l2")
    if st.button("ENTRAR", key="btn_l"):
        if s_dig == USUARIOS[n_sel]["senha"]:
            st.session_state.cozinheiro = USUARIOS[n_sel]["nome"]
            st.session_state.navio = n_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("❌ Senha incorreta")

# --- MENU (SEMPRE LARANJA) ---
elif st.session_state.pagina == "menu":
    st.markdown("<style>.stApp { background-color: #FF8C00; } button { background-color: white !important; color: black !important; }</style>", unsafe_allow_html=True)
    st.title(f"🚢 Painel - {st.session_state.navio}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True, key="m1"): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True, key="m2"): st.session_state.pagina = "historico"; st.rerun()
    with c2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True, key="m3"): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.session_state.navio == "ADMIN":
            if st.button("👑 PAINEL ADM", use_container_width=True, key="m4"): st.session_state.pagina = "admin"; st.rerun()
    if st.button("⬅️ SAIR", key="m5"): st.session_state.pagina = "home"; st.rerun()

# --- TABELA DE RANCHO (TÍTULO VERDE / FUNDO ESTOQUE) ---
elif st.session_state.pagina == "lista":
    st.markdown("""<style>
        .stApp { background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); background-size: cover; }
        h1 { color: #00FF00 !important; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        label { color: white !important; }
    </style>""", unsafe_allow_html=True)
    st.title("📋 Conferência de Estoque")
    
    if st.button("🔄 ATUALIZAR NOTION", key="upd"):
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
        res = requests.post(url, headers=headers)
        if res.status_code == 200:
            dados = []
            for p in res.json().get("results", []):
                prop = p.get("properties", {})
                dados.append({
                    "ITEM": prop.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": prop.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": prop.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": prop.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": prop.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            st.session_state.df_lista = pd.DataFrame(dados)
            st.rerun()

    if not st.session_state.df_lista.empty:
        df_ed = st.data_editor(st.session_state.df_lista, hide_index=True, use_container_width=True, key="ed_r")
        if st.button("📥 SALVAR E GERAR PDF DO RANCHO", key="pdf_r"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Checklist de Rancho", ln=True, align="C")
            st.download_button("Baixar PDF", pdf.output(dest='S').encode('latin-1'), "rancho.pdf")

    if st.button("⬅️ VOLTAR", key="v_r"): st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 3: TELA DE DECLARAÇÃO E REGISTRO (RESTAURADA) ---
elif st.session_state.pagina == "tripulacao":
    # CSS Restaurado do seu código original (Anexo 2)
    st.markdown("""
        <style>
        .stApp { 
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
            url("https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?q=80&w=1920"); 
            background-size: cover; 
            background-position: center;
        }
        /* Letras de Comando Maiores conforme solicitado */
        label p { 
            font-size: 1.4rem !important; 
            color: white !important; 
            font-weight: bold !important;
            text-shadow: 2px 2px 4px black;
        }
        /* Campos Brancos com Letras Pretas */
        .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input { 
            color: black !important; 
            background-color: white !important; 
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 3px 3px 6px black;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)

    # Lógica de Escolta e Advertência Dinâmica
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True)
    dias_duracao = 12 if escolta == "SIM" else 15
    
    col_v1, col_v2 = st.columns([1, 1.5])
    with col_v1:
        dt_recebimento = st.date_input("Data prevista para o rancho:", datetime.now())
    
    with col_v2:
        dt_validade = dt_recebimento + timedelta(days=dias_duracao)
        # Cor dinâmica: Vermelho para Escolta (Atenção), Verde para Normal
        cor_alerta = "#FF3131" if escolta == "SIM" else "#00D100"
        st.markdown(f"""
            <div style='background-color:{cor_alerta}; padding:18px; border-radius:12px; color:black; font-weight:900; text-align:center; border: 2px solid black; font-size: 1.2rem;'>
                ATENÇÃO: Com {dias_duracao} dias, seu rancho durará até {dt_validade.strftime('%d/%m/%Y')}
            </div>
            """, unsafe_allow_html=True)

    # Formulário de Registro (Baseado no seu algoritmo pronto)
    with st.form("form_declaracao_oficial", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            lotacao = st.number_input("Número de Tripulantes:", min_value=1, value=16)
            origem = st.text_input("Porto de Origem:", value="Porto Velho")
        with c2:
            dt_ultimo = st.date_input("Data do último rancho:", datetime.now())
            destino = st.text_input("Porto de Destino:", value="Novo Remanso")
        
        necessidades = st.text_area("Necessidades Extras:", placeholder="Descreva aqui...")
        
        st.write("Assinatura Digital:")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFF", height=120, key="assinatura")
        
        # Botão de Ação do Form
        btn_gravar = st.form_submit_button("💾 REGISTRAR NO HISTÓRICO E GERAR PDF")

    # PROCESSAMENTO PÓS-SUBMIT (Fora do form para evitar erro de PDF)
    if btn_gravar:
        # 1. Envio para o Notion (Seu algoritmo original)
        payload = {
            "parent": {"database_id": ID_HISTORICO_NOTION},
            "properties": {
                "Cozinheiro": {"title": [{"text": {"content": st.session_state.cozinheiro}}]},
                "Navio": {"rich_text": [{"text": {"content": st.session_state.navio}}]},
                "Data Pedido": {"date": {"start": dt_recebimento.strftime("%Y-%m-%d")}},
                "Validade": {"date": {"start": dt_validade.strftime("%Y-%m-%d")}}
            }
        }
        
        try:
            h_notion = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
            res = requests.post("https://api.notion.com/v1/pages", headers=h_notion, json=payload)
            if res.status_code == 200:
                st.success("✅ Histórico Gravado com Sucesso!")
            else:
                st.error(f"Erro ao gravar histórico: {res.status_code}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

        # 2. Geração do PDF (Layout que você já usava)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "DECLARACAO DE REABASTECIMENTO", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, f"Navio: {st.session_state.navio}\nResponsavel: {st.session_state.cozinheiro}\nPrevisao: {dt_recebimento}\nValidade: {dt_validade}")
        
        # O botão de download aparece aqui, fora do st.form
        st.download_button(
            label="📥 CLIQUE AQUI PARA BAIXAR O PDF",
            data=pdf.output(dest='S').encode('latin-1'),
            file_name=f"Declaracao_{st.session_state.navio}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.button("⬅️ VOLTAR AO MENU", key="v_t"):
        st.session_state.pagina = "menu"
        st.rerun()        
# --- HISTÓRICO (AGORA ATIVO) ---
elif st.session_state.pagina == "historico":
    st.markdown("<style>.stApp { background-color: #FF8C00; }</style>", unsafe_allow_html=True)
    st.title(f"📜 Histórico - {st.session_state.navio}")
    
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    res = requests.post(f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query", headers=headers)
    if res.status_code == 200:
        dados_h = []
        for r in res.json().get("results", []):
            p = r["properties"]
            navio_reg = p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else ""
            if navio_reg == st.session_state.navio or st.session_state.navio == "ADMIN":
                dados_h.append({
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "",
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "",
                    "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else ""
                })
        st.dataframe(pd.DataFrame(dados_h), use_container_width=True)
    
    if st.button("⬅️ VOLTAR", key="v_h"): st.session_state.pagina = "menu"; st.rerun()
