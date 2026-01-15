import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# --- CONFIGURAÇÃO PARA ÍCONE E APP INSTALÁVEL (PWA) ---
st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json?v=10">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="icon" type="image/png" href="./logo_pwa.png">
        <link rel="apple-touch-icon" href="./logo_pwa.png">
    </head>
    """, unsafe_allow_html=True)
# -----------------------------------------------------

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, CONSTANTES E ESTADOS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "JATOBA": {"nome": "CZA AUGUSTO", "senha": "5881"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "ADMINISTRADOR": {"nome": "ALEX", "senha": "2463"}
}

# =================================================================
# BLOCO 2: FUNÇÕES DE SUPORTE E CONEXÕES (API)
# =================================================================
def carregar_dados_do_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            dados = []
            for page in results:
                p = page.get("properties", {})
                dados.append({
                    "ITEM": p.get("ITEM", {}).get("title", [{}])[0].get("plain_text", ""),
                    "DESCRIÇÃO": p.get("DESCRIÇÃO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "TIPO": p.get("TIPO", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "UNID MED": p.get("UNID MED", {}).get("rich_text", [{}])[0].get("plain_text", ""),
                    "PREDEFINIDO": p.get("PREDEFINIDO", {}).get("number", 0),
                    "CONFIRMA": 0
                })
            df = pd.DataFrame(dados)
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except: return st.session_state.df_lista

def aplicar_estilo_azul():
    st.markdown("<style>.stApp { background-color: #4169E1 !important; } h1,h2,h3,p,label { color: white !important; } div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900; border-radius: 10px; }</style>", unsafe_allow_html=True)

# =================================================================
# BLOCO 3: TELA HOME (INICIAL) - AJUSTE DE PROPORÇÃO
# =================================================================
import base64

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

if st.session_state.pagina == "home":
    # Converte a imagem para Base64 para garantir que o Streamlit exiba
    img_base64 = get_base64_of_bin_file('zion_final.jpg')
    
    st.markdown(f"""
        <style>
        .stApp {{
            /* Mantém a cor escura de fundo caso a imagem demore a carregar */
            background-color: #0e1117;
            
            /* Ajuste da Imagem: 'contain' faz ela caber inteira, 'cover' preenche tudo */
            background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                              url("data:image/jpg;base64,{img_base64}");
            
            background-size: contain; /* Ajusta a imagem para aparecer inteira */
            background-repeat: no-repeat;
            background-position: center top; /* Alinha no topo para dar espaço ao botão */
            background-attachment: fixed;
        }}
        
        .main-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end; /* Empurra o conteúdo para baixo */
            height: 85vh; /* Altura da área visível */
            padding-bottom: 50px;
        }}

        div.stButton > button {{
            width: 280px !important;
            height: 60px !important;
            background-color: #FF8C00 !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: bold !important;
            font-size: 22px !important;
            border: 2px solid rgba(255,255,255,0.3) !important;
            box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
            transition: 0.3s;
        }}
        
        div.stButton > button:hover {{
            transform: scale(1.05);
            background-color: #ff9900 !important;
        }}
        </style>
        """, unsafe_allow_html=True)

    # Container principal
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Espaçador para o botão não ficar em cima do nome ZION da imagem
    st.markdown("<div style='margin-top: 400px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 ACESSAR SISTEMA"): 
        st.session_state.pagina = "login"
        st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
elif st.session_state.pagina == "login":
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("https://images.unsplash.com/photo-1574689049868-e94ed5301745?q=80&w=1920");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .login-box {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1, h2, label {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
        div.stButton > button {
            width: 100% !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    
    with col_l2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        navio_sel = st.selectbox("Selecione sua Embarcação", list(USUARIOS.keys()))
        senha_dig = st.text_input("Senha de Acesso", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 ENTRAR"):
            dados = USUARIOS.get(navio_sel)
            if dados and senha_dig == dados["senha"]:
                st.session_state.cozinheiro = dados["nome"]
                st.session_state.navio = navio_sel
                st.session_state.mensagem_boas_vindas = f"Seja bem vindo ao Zion {dados['nome']}, vamos fazer o seu pedido."
                st.session_state.pagina = "menu"
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
        
        if st.button("⬅️ VOLTAR AO INÍCIO"):
            st.session_state.pagina = "home"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    
    if 'mensagem_boas_vindas' in st.session_state:
        st.success(st.session_state.mensagem_boas_vindas)
    
    st.title(f"🚢 Painel - {st.session_state.navio}")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): 
            st.session_state.pagina = "lista"
            st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): 
            st.session_state.pagina = "historico"
            st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): 
            st.session_state.pagina = "tripulacao"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ LOGOUT (SAIR)"): 
        st.session_state.pagina = "home"
        st.rerun()

elif st.session_state.pagina == "lista":
    import io
    from datetime import datetime, timedelta
    import unicodedata

    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                        url("https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        .btn-export {
            background-color: white !important; color: #004aad !important;
            border-radius: 10px !important; font-weight: bold !important;
            border: 1px solid #004aad !important;
        }
        div.stButton > button {
            background-color: #004aad !important; color: white !important;
            border-radius: 20px !important; font-weight: bold !important;
        }
        .stDataFrame { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        h1, h2, h3, p, label { color: white !important; text-shadow: 2px 2px 5px black; }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    
    col_refresh, col_spacer = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 ATUALIZAR TABELA", use_container_width=True):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.toast("Dados sincronizados!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    pode_exportar = True 
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("COD", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("LIMITE", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("NECESSIDADE", min_value=0),
        },
        hide_index=True, use_container_width=True, key="editor_estoque_final"
    )

    itens_excedentes = df_editado[df_editado["CONFIRMA"] > df_editado["PREDEFINIDO"]]
    if not itens_excedentes.empty:
        pode_exportar = False
        st.error("⚠️ BLOQUEIO: VALOR ACIMA DO LIMITE PERMITIDO!")

    st.markdown("---")
    
    col_pdf, col_excel, col_menu = st.columns(3)
    
    with col_pdf:
        if pode_exportar:
            try:
                def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')
                
                class PDF_Checklist(FPDF):
                    def header(self):
                        if os.path.exists("zion3.jpg"): self.image("zion3.jpg", 95, 8, 20)
                        self.set_font("Arial", "B", 14); self.ln(22)
                        self.cell(0, 10, preparar(f"Checklist de Rancho: {st.session_state.navio}"), ln=True, align="C")
                        self.ln(5)
                        self.set_fill_color(200, 200, 200); self.set_font("Arial", "B", 8)
                        self.cell(10, 7, "COD", 1, 0, "C", True)
                        self.cell(30, 7, "TIPO", 1, 0, "C", True)
                        self.cell(15, 7, "UNID", 1, 0, "C", True)
                        self.cell(15, 7, "PREDEF", 1, 0, "C", True)
                        self.cell(105, 7, "DESCRICAO", 1, 0, "C", True)
                        self.cell(15, 7, "CONF.", 1, 1, "C", True)
                    
                    def footer(self):
                        self.set_y(-15); self.set_font('Arial', 'I', 8)
                        fuso_brasilia = datetime.now() - timedelta(hours=3)
                        data_hora = fuso_brasilia.strftime("%d/%m/%Y %H:%M:%S")
                        texto = f"Gerado em: {data_hora} (Brasília) - Pagina {self.page_no()}"
                        self.cell(0, 10, preparar(texto), 0, 0, 'C')

                pdf = PDF_Checklist()
                pdf.add_page(); pdf.set_font("Arial", "", 8)
                for _, r in df_editado.iterrows():
                    pdf.cell(10, 6, str(r["ITEM"]), 1, 0, "C")
                    pdf.cell(30, 6, preparar(r["TIPO"]), 1, 0, "L")
                    pdf.cell(15, 6, preparar(r["UNID MED"]), 1, 0, "C")
                    pdf.cell(15, 6, str(r["PREDEFINIDO"]), 1, 0, "C")
                    pdf.cell(105, 6, preparar(r["DESCRIÇÃO"]), 1, 0, "L")
                    pdf.cell(15, 6, str(r["CONFIRMA"]), 1, 1, "C")

                st.download_button(
                    label="📄 BAIXAR PDF", 
                    data=pdf.output(dest='S').encode('latin-1'), 
                    file_name=f"Checklist_{st.session_state.navio}.pdf", 
                    mime="application/pdf", 
                    use_container_width=True
                )
            except Exception as e: st.error(f"Erro no PDF: {e}")

    with col_excel:
        if pode_exportar:
            try:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_editado.to_excel(writer, index=False, sheet_name='Rancho')
                st.download_button(
                    label="📊 BAIXAR EXCEL", 
                    data=output.getvalue(), 
                    file_name=f"Rancho_{st.session_state.navio}.xlsx", 
                    use_container_width=True
                )
            except: st.error("Erro ao gerar Excel.")

    with col_menu:
        if st.button("⬅️ MENU PRINCIPAL", use_container_width=True):
            st.session_state.pagina = "menu"; st.rerun() 

# =================================================================
# BLOCO 7: TELA DE DECLARAÇÃO (VERSÃO FINAL COMPLETA E RESTAURADA)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    import requests
    from datetime import datetime, timedelta
    import unicodedata
    import pytz
    import base64
    from io import BytesIO
    from PIL import Image
    from fpdf import FPDF
    from streamlit_drawable_canvas import st_canvas

    st.markdown("""
        <style>
        .stApp { background-color: #3b66eb !important; }
        h1, h2, h3, p, label, .stMarkdown, span { color: #ffffff !important; }
        input, div[data-baseweb="input"], textarea, div[data-baseweb="select"] {
            background-color: #ffffff !important; color: #1a365d !important; border-radius: 8px !important;
        }
        div.stButton > button {
            border-radius: 10px; border: 2px solid #ffffff; background-color: transparent;
            color: #ffffff; font-weight: bold; transition: all 0.3s;
        }
        div.stButton > button:hover { background-color: #ffffff; color: #3b66eb; }
        .stForm { background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; }
        </style>
    """, unsafe_allow_html=True)

    c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
    with c_nav1:
        if st.button("⬅️ MENU", use_container_width=True):
            st.session_state.pagina = "menu"; st.rerun()
    with c_nav3:
        if st.button("🚪 SAIR", use_container_width=True):
            st.session_state.pagina = "login"; st.rerun()

    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    col_esc, col_val = st.columns([2, 2])
    with col_esc:
        escolta_sel = st.radio("O navio está com escolta?", ["NÃO", "SIM"], index=0, horizontal=True)
        dias_duracao = 12 if escolta_sel == "SIM" else 15
    
    with col_val:
        data_recebimento = st.date_input("Data prevista para o novo rancho:", datetime.now(), format="DD/MM/YYYY")
        data_validade = data_recebimento + timedelta(days=dias_duracao)
        st.info(f"📅 Validade: {data_validade.strftime('%d/%m/%Y')} ({dias_duracao} dias)")

    with st.form("form_declaracao_v11_restaurado"):
        c1, c2 = st.columns(2)
        with c1:
            resp_nome = st.text_input("Responsável", value=st.session_state.get('cozinheiro', 'CZA AUGUSTO'), disabled=True)
            navio_nome = st.text_input("Navio", value=st.session_state.get('navio', 'JATOBA'), disabled=True)
            origem = st.text_input("Porto de Origem", value="Porto Velho")
            # CAMPO RESTAURADO
            data_ultimo = st.date_input("Data do último rancho:", format="DD/MM/YYYY")
        with c2:
            qtde_trip = st.number_input("Qtde Tripulante:", min_value=1, value=16)
            destino = st.text_input("Porto de Destino", value="Novo remanso")
        
        campo_consideracoes = st.text_area("Considerações (Apenas PDF):", value="Consumo regular conforme escala.")
        
        st.write("Assinatura Digital:")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#FFFFFF",
            height=120, drawing_mode="freedraw", key="canvas_v11_rest"
        )
        
        btn_acao = st.form_submit_button("💾 SALVAR E GERAR PDF", use_container_width=True)

    if btn_acao:
        if canvas_result.image_data is not None:
            try:
                # 1. PROCESSAR ASSINATURA (COMPRESSÃO PARA O NOTION)
                img_raw = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_notion = img_raw.resize((80, 30), Image.LANCZOS)
                buf_n = BytesIO()
                img_notion.convert("RGB").save(buf_n, format="JPEG", quality=15)
                img_str_curta = base64.b64encode(buf_n.getvalue()).decode()
                img_raw.save("temp_sign.png")

                # 2. GERAR PDF
                pdf = FPDF()
                pdf.add_page()
                def f(t): return unicodedata.normalize('NFKD', str(t or "")).encode('latin-1', 'ignore').decode('latin-1')
                
                pdf.set_font("Arial", "B", 35); pdf.set_text_color(0, 51, 153); pdf.cell(0, 20, "ZION", ln=True, align="C")
                pdf.set_font("Arial", "B", 14); pdf.set_text_color(0, 0, 0); pdf.cell(0, 10, f("MAPA DE TRIPULÇÃO"), ln=True, align="C"); pdf.ln(10)
                
                pdf.set_font("Arial", "", 12)
                corpo = (f"Pelo presente, certifico que a lotacao de tripulantes a bordo do empurrador {navio_nome} e de {qtde_trip} tripulantes. "
                         f"A provisao de rancho destina-se a cobrir as necessidades por {dias_duracao} dias. "
                         f"Ultimo rancho em: {data_ultimo.strftime('%d/%m/%Y')}. Validade ate {data_validade.strftime('%d/%m/%Y')}.")
                pdf.multi_cell(0, 10, f(corpo))
                
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f(f"Origem: {origem} | Destino: {destino}"), ln=True)
                pdf.cell(0, 8, f(f"Escolta no Navio: {escolta_sel}"), ln=True)
                
                if campo_consideracoes:
                    pdf.ln(5); pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, f("Consideracoes:"), ln=True)
                    pdf.set_font("Arial", "", 12); pdf.multi_cell(0, 8, f(campo_consideracoes))
                
                pdf.ln(25)
                pdf.image("temp_sign.png", x=75, w=60) 
                pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
                pdf.set_font("Arial", "B", 12); pdf.cell(0, 7, f(resp_nome), ln=True, align="C")
                
                # Fuso horário Brasil
                fuso = pytz.timezone('America/Sao_Paulo')
                agora = datetime.now(fuso)
                txt_data_hora = agora.strftime('%d/%m/%Y às %H:%M:%S')
                pdf.set_font("Arial", "I", 9); pdf.cell(0, 5, f(f"Assinado em: {txt_data_hora}"), ln=True, align="C")

                pdf_bytes = pdf.output(dest='S').encode('latin-1')

                # 3. NOTION (ENVIANDO TUDO CONFORME COMBINADO)
                headers_n = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
                payload_n = {
                    "parent": {"database_id": ID_HISTORICO_NOTION},
                    "properties": {
                        "Responsável": {"title": [{"text": {"content": str(resp_nome)}}]},
                        "Navio": {"rich_text": [{"text": {"content": str(navio_nome)}}]},
                        "Novo Rancho": {"date": {"start": data_recebimento.isoformat()}},
                        "Validade": {"date": {"start": data_validade.isoformat()}},
                        "Qtde Tripulante": {"number": int(qtde_trip)},
                        "Escolta": {"rich_text": [{"text": {"content": str(escolta_sel)}}]},
                        "Porto de Origem": {"rich_text": [{"text": {"content": str(origem)}}]},
                        "Porto de Destino": {"rich_text": [{"text": {"content": str(destino)}}]},
                        "Assinatura": {"rich_text": [{"text": {"content": str(img_str_curta)}}]}
                    }
                }
                
                res_n = requests.post("https://api.notion.com/v1/pages", headers=headers_n, json=payload_n)
                
                if res_n.status_code == 200:
                    st.success("✅ Tudo ok! PDF e Notion atualizados.")
                    st.download_button("📥 BAIXAR PDF", data=pdf_bytes, file_name=f"Declaracao_{navio_nome}.pdf", use_container_width=True)
                else:
                    st.error(f"Erro Notion: {res_n.json().get('message')}")
                    st.download_button("📥 BAIXAR PDF (Mesmo com erro)", data=pdf_bytes, file_name="Declaracao.pdf", use_container_width=True)

            except Exception as e:
                st.error(f"Erro: {e}")
# =================================================================
# BLOCO 8: HISTÓRICO - CABEÇALHO ATUALIZADO E ASSINATURA NÍTIDA
# =================================================================
elif st.session_state.pagina == "historico":
    import requests
    from datetime import datetime
    import unicodedata
    import pytz
    import base64
    from io import BytesIO
    from PIL import Image
    from fpdf import FPDF

    st.markdown("""
        <style>
        .stApp { background-color: #3b66eb !important; }
        h1, h2, h3, p, label, .stMarkdown, span { color: #ffffff !important; }
        div.stButton > button {
            border-radius: 10px; border: 2px solid #ffffff; background-color: transparent;
            color: #ffffff; font-weight: bold; transition: all 0.3s;
        }
        div.stButton > button:hover { background-color: #ffffff; color: #3b66eb; }
        </style>
    """, unsafe_allow_html=True)

    if st.button("⬅️ MENU PRINCIPAL"):
        st.session_state.pagina = "menu"; st.rerun()

    st.markdown("<h1 style='text-align: center;'>🗄️ Histórico de Documentos</h1>", unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        data_de = st.date_input("De:", datetime.now() - timedelta(days=30), format="DD/MM/YYYY")
    with col_f2:
        data_ate = st.date_input("Até:", datetime.now(), format="DD/MM/YYYY")
    
    if col_f3.button("🔍 CONSULTAR", use_container_width=True):
        headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
        query = {
            "filter": {
                "and": [
                    {"property": "Novo Rancho", "date": {"on_or_after": data_de.isoformat()}},
                    {"property": "Novo Rancho", "date": {"on_or_before": data_ate.isoformat()}}
                ]
            },
            "sorts": [{"property": "Novo Rancho", "direction": "descending"}]
        }
        res = requests.post(f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query", headers=headers, json=query)
        if res.status_code == 200:
            st.session_state.dados_historico = res.json().get("results", [])
        else:
            st.error("Erro ao buscar dados.")

    if "dados_historico" in st.session_state:
        for p in st.session_state.dados_historico:
            props = p.get("properties", {})
            try:
                h_resp = props["Responsável"]["title"][0]["text"]["content"]
                h_navio = props["Navio"]["rich_text"][0]["text"]["content"]
                h_data_raw = props["Novo Rancho"]["date"]["start"]
                h_data_f = datetime.strptime(h_data_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
                h_validade = props["Validade"]["date"]["start"] if props["Validade"]["date"] else "N/A"
                h_validade_f = datetime.strptime(h_validade, "%Y-%m-%d").strftime("%d/%m/%Y") if h_validade != "N/A" else "N/A"
                h_trip = props["Qtde Tripulante"]["number"]
                h_origem = props["Porto de Origem"]["rich_text"][0]["text"]["content"]
                h_destino = props["Porto de Destino"]["rich_text"][0]["text"]["content"]
                h_escolta = props["Escolta"]["rich_text"][0]["text"]["content"] if props["Escolta"]["rich_text"] else "NÃO"
                h_sign_base64 = props["Assinatura"]["rich_text"][0]["text"]["content"]
            except: continue

            with st.expander(f"🚢 {h_navio} | 📅 {h_data_f} | 👤 {h_resp}"):
                if st.button(f"📄 GERAR 2ª VIA PDF - {p['id'][:5]}", key=p['id']):
                    try:
                        # MELHORIA NA ASSINATURA: Reconstituir com mais nitidez
                        sign_data = base64.b64decode(h_sign_base64)
                        img_sig = Image.open(BytesIO(sign_data)).convert("RGB")
                        # Redimensionamento suave para manter bordas limpas
                        img_sig = img_sig.resize((300, 120), Image.LANCZOS) 
                        img_sig.save("temp_2via_sign.png", "PNG", quality=100)

                        pdf = FPDF()
                        pdf.add_page()
                        def f(t): return unicodedata.normalize('NFKD', str(t or "")).encode('latin-1', 'ignore').decode('latin-1')
                        
                        # CABEÇALHO ATUALIZADO
                        pdf.set_font("Arial", "B", 35); pdf.set_text_color(0, 51, 153); pdf.cell(0, 20, "ZION", ln=True, align="C")
                        pdf.set_font("Arial", "B", 16); pdf.set_text_color(0, 0, 0); pdf.cell(0, 10, f("MAPA DE TRIPULACÃO"), ln=True, align="C")
                        pdf.set_font("Arial", "I", 12); pdf.cell(0, 7, f("2 via"), ln=True, align="C"); pdf.ln(10)
                        
                        pdf.set_font("Arial", "", 12)
                        corpo = (f"Certifico que a lotacao de tripulantes a bordo do empurrador {h_navio} e de {h_trip} tripulantes. "
                                 f"Pedido original de {h_data_f}, com validade ate {h_validade_f}.")
                        pdf.multi_cell(0, 10, f(corpo))
                        
                        pdf.ln(5); pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 8, f(f"Origem: {h_origem} | Destino: {h_destino}"), ln=True)
                        pdf.cell(0, 8, f(f"Escolta no Navio: {h_escolta}"), ln=True)
                        
                        # RODAPÉ COM ASSINATURA NÍTIDA
                        pdf.ln(25)
                        pdf.image("temp_2via_sign.png", x=75, w=60) 
                        pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
                        pdf.set_font("Arial", "B", 12); pdf.cell(0, 7, f(h_resp), ln=True, align="C")
                        
                        fuso = pytz.timezone('America/Sao_Paulo')
                        agora = datetime.now(fuso)
                        pdf.set_font("Arial", "I", 9); pdf.cell(0, 5, f(f"2a Via emitida em: {agora.strftime('%d/%m/%Y as %H:%M:%S')}"), ln=True, align="C")

                        pdf_bytes = pdf.output(dest='S').encode('latin-1')
                        st.download_button("📥 BAIXAR 2ª VIA", data=pdf_bytes, file_name=f"2via_{h_navio}.pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"Erro ao gerar: {e}")
