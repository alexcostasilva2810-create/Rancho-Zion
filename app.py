import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
def carregar_dados_do_notion():
    # Esta função usa o ID do seu banco de dados para trazer a lista completa
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    try:
        res = requests.post(url, headers=headers)
        data = res.json()
        lista_completa = []
        for page in data["results"]:
            props = page["properties"]
            lista_completa.append({
                "ITEM": props["ITEM"]["title"][0]["text"]["content"] if props["ITEM"]["title"] else "",
                "DESCRIÇÃO": props["DESCRIÇÃO"]["rich_text"][0]["text"]["content"] if props["DESCRIÇÃO"]["rich_text"] else "",
                "TIPO": props["TIPO"]["select"]["name"] if props["TIPO"]["select"] else "",
                "UNID MED": props["UNID MED"]["rich_text"][0]["text"]["content"] if props["UNID MED"]["rich_text"] else "",
                "PREDEFINIDO": props["PREDEFINIDO"]["number"] if "PREDEFINIDO" in props and props["PREDEFINIDO"]["number"] is not None else 0,
                "CONFIRMA": 0 
            })
        return pd.DataFrame(lista_completa).sort_values(by="ITEM")
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return pd.DataFrame()

# =================================================================
# BLOCO 1: CONFIGURAÇÕES E IDs
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

def carregar_dados_do_notion():
    # Esta função garante que busque TUDO do seu Notion
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    try:
        res = requests.post(url, headers=headers)
        data = res.json()
        lista_completa = []
        for page in data["results"]:
            props = page["properties"]
            lista_completa.append({
                "ITEM": props["ITEM"]["title"][0]["text"]["content"] if props["ITEM"]["title"] else "",
                "DESCRIÇÃO": props["DESCRIÇÃO"]["rich_text"][0]["text"]["content"] if props["DESCRIÇÃO"]["rich_text"] else "",
                "TIPO": props["TIPO"]["select"]["name"] if props["TIPO"]["select"] else "",
                "UNID MED": props["UNID MED"]["rich_text"][0]["text"]["content"] if props["UNID MED"]["rich_text"] else "",
                "PREDEFINIDO": props["PREDEFINIDO"]["number"] if "PREDEFINIDO" in props and props["PREDEFINIDO"]["number"] else 0,
                "CONFIRMA": 0 
            })
        return pd.DataFrame(lista_completa).sort_values(by="ITEM")
    except:
        return pd.DataFrame()

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

# --- BLOCO 6: TELA DE LISTA (CONFERÊNCIA DE ESTOQUE) ---
# Configuração visual para não cortar a tabela
    st.markdown("""<style>
        .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920"); background-size: cover; }
        .pdf-frame { border: 2px solid white; border-radius: 10px; background: white; }
    </style>""", unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white;'>📋 Conferência de Estoque</h1>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("⬅️ VOLTAR"):
            st.session_state.pagina = "menu"; st.rerun()
    with c2:
        if st.button("🔄 SINCRONIZAR TUDO DO NOTION"):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.rerun()

    col_pdf, col_tabela = st.columns([1, 1.2])

    with col_pdf:
        st.markdown("<h4 style='color: white;'>📄 Documento Original</h4>", unsafe_allow_html=True)
        if os.path.exists("Rancho_JACARANDA.pdf"):
            with open("Rancho_JACARANDA.pdf", "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" class="pdf-frame"></iframe>', unsafe_allow_html=True)

    with col_tabela:
        st.markdown("<h4 style='color: white;'>📝 Itens do Notion</h4>", unsafe_allow_html=True)
        if 'df_lista' not in st.session_state or st.session_state.df_lista.empty:
            st.session_state.df_lista = carregar_dados_do_notion()

        # Altura de 800 para mostrar todos os itens do PDF (Carne Moída até o Gás)
        st.data_editor(
            st.session_state.df_lista,
            column_config={
                "ITEM": st.column_config.TextColumn("COD", disabled=True),
                "DESCRIÇÃO": st.column_config.TextColumn("PRODUTO", disabled=True),
                "PREDEFINIDO": st.column_config.NumberColumn("SOLIC.", disabled=True),
                "CONFIRMA": st.column_config.NumberColumn("REC.", min_value=0)
            },
            hide_index=True,
            use_container_width=True,
            height=800 
        )
        if st.button("💾 FINALIZAR E SALVAR"):
            st.success("Conferência completa salva com sucesso!")
# --- BLOCO 3: TELA DE DECLARAÇÃO (RESTAURADA COM ALERTA DE ENVIO) ---
elif st.session_state.pagina == "tripulacao":
    st.markdown("""
        <style>
        .stApp { 
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
            url("https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?q=80&w=1920"); 
            background-size: cover; background-position: center;
        }
        label p { font-size: 1.4rem !important; color: white !important; font-weight: bold !important; text-shadow: 2px 2px 4px black; }
        .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input { 
            color: black !important; background-color: white !important; font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 3px 3px 6px black;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)

    # Configuração de Escolta e Alerta de Validade
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True, key="escolta_v5")
    dias_duracao = 12 if escolta == "SIM" else 15
    
    col_v1, col_v2 = st.columns([1, 1.5])
    with col_v1:
        dt_recebimento = st.date_input("Data prevista para o rancho:", datetime.now())
    with col_v2:
        dt_validade = dt_recebimento + timedelta(days=dias_duracao)
        cor_alerta = "#FF3131" if escolta == "SIM" else "#00D100"
        st.markdown(f"""
            <div style='background-color:{cor_alerta}; padding:18px; border-radius:12px; color: black; font-weight: 900; text-align:center; border: 3px solid black; font-size: 1.3rem;'>
                ATENÇÃO: Rancho durará até {dt_validade.strftime('%d/%m/%Y')}
            </div>
            """, unsafe_allow_html=True)

    with st.form("form_declaracao_final_v3"):
        c1, c2 = st.columns(2)
        with c1:
            lotacao = st.number_input("Número de Tripulantes:", min_value=1, value=16)
            origem = st.text_input("Porto de Origem:", value="Porto Velho")
        with c2:
            dt_ultimo = st.date_input("Data do último rancho:", datetime.now())
            destino = st.text_input("Porto de Destino:", value="Novo Remanso")
        
        necessidades = st.text_area("Necessidades Extras:", value="No rancho pelo fato da baixa do rio. Por gentileza colocar 06 vassoura, 06 rodo, 02 pá de lixo de ferro...")
        st.write("Assinatura Digital:")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFF", height=150, key="sign_v5")
        btn_gravar = st.form_submit_button("💾 SALVAR E GERAR PDF OFICIAL")

    if btn_gravar:
        # Gravação no Notion
        try:
            h_notion = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
            body = {"parent": {"database_id": ID_HISTORICO_NOTION}, "properties": {
                "Cozinheiro": {"title": [{"text": {"content": st.session_state.cozinheiro}}]},
                "Navio": {"rich_text": [{"text": {"content": st.session_state.navio}}]},
                "Data Pedido": {"date": {"start": dt_recebimento.strftime("%Y-%m-%d")}},
                "Validade": {"date": {"start": dt_validade.strftime("%Y-%m-%d")}}
            }}
            requests.post("https://api.notion.com/v1/pages", headers=h_notion, json=body)
        except: pass

        # GERAÇÃO DO PDF
        class PDF(FPDF):
            def header(self):
                if os.path.exists("ZION.jpg"): self.image("ZION.jpg", 90, 8, 30)
                self.ln(35)
                self.set_font("Arial", "B", 16)
                self.cell(0, 10, "DECLARACAO DE REABASTECIMENTO", ln=True, align="C")
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, f"Embarcacao: {st.session_state.navio.upper()}", ln=True, align="C")
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.cell(0, 10, f"Gerado em: {data_hora} - Pagina {self.page_no()}", align="C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 11)
        texto_legal = (f"Pelo presente, certifico que a lotacao de tripulantes a bordo do empurrador e de {lotacao} tripulantes. "
                       f"A provisao de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da tripulacao "
                       f"por um periodo de {dias_duracao} dias nauticos a partir de {dt_recebimento.strftime('%d/%m/%Y')}. ")
        pdf.multi_cell(0, 8, texto_legal)
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"Origem: {origem} | Destino: {destino}", ln=True)
        pdf.cell(0, 8, f"Ultimo Rancho: {dt_ultimo.strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 8, "CONSIDERACOES:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, necessidades)
        
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            img.save("temp_sign.png")
            pdf.image("temp_sign.png", x=60, y=pdf.get_y() + 5, w=80)
        
        pdf.ln(35)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 0, "________________________________________________", ln=True, align="C")
        pdf.ln(5)
        pdf.cell(0, 8, f"{st.session_state.cozinheiro.upper()}", ln=True, align="C")

        # --- NOVO AJUSTE: ALERTA VERDE APÓS SALVAR ---
        st.markdown(f"""
            <div style='background-color:#00D100; padding:20px; border-radius:10px; color: black; font-weight: bold; text-align:center; border: 2px solid black; margin-bottom: 15px;'>
                ✅ REGISTRO SALVO! AGORA BAIXE O PDF ABAIXO E ENVIE AO COMPRADOR IMEDIATAMENTE.
            </div>
            """, unsafe_allow_html=True)

        st.download_button(
            label="📥 BAIXAR DECLARAÇÃO PDF OFICIAL",
            data=pdf.output(dest='S').encode('latin-1'),
            file_name=f"Declaracao_{st.session_state.navio}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()
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
