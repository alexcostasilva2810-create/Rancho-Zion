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
# BLOCO 3: TELA HOME (INICIAL) - AJUSTE OFFSHORE E LOGO
# =================================================================
if st.session_state.pagina == "home":
    # CSS para fundo Offshore Petrolífero e alinhamento de títulos
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
                        url("https://images.unsplash.com/photo-1574689049868-e94ed5301745?q=80&w=1920");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-top: -50px;
        }
        .titulo-zion {
            color: white !important;
            font-size: 50px !important;
            font-weight: 800 !important;
            text-shadow: 4px 4px 15px rgba(0,0,0,0.9);
            margin-bottom: -15px !important; /* Aproxima o nome da logo */
            font-family: 'Helvetica', sans-serif;
        }
        /* Ajuste do botão */
        div.stButton > button {
            width: 200px !important;
            height: 45px !important;
            background-color: #FF8C00 !important;
            color: white !important;
            border-radius: 25px !important;
            font-weight: bold !important;
            border: none !important;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #e67e00 !important;
            transform: scale(1.05);
        }
        </style>
        """, unsafe_allow_html=True)

    # Container principal para centralização
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Nome centralizado exatamente sobre a imagem
    st.markdown("<h1 class='titulo-zion'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    
    # Colunas para centralizar a sua logo ZION.jpg
    col1, col2, col3 = st.columns([1, 0.6, 1])
    with col2:
        if os.path.exists("ZION.jpg"): 
            st.image("ZION.jpg", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão de acesso centralizado e curto
    col_btn1, col_btn2, col_btn3 = st.columns([1.4, 1, 1.4])
    with col_btn2:
        if st.button("🚀 ACESSAR"): 
            st.session_state.pagina = "login"
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
# =================================================================
# BLOCO 4: TELA DE LOGIN (COM FUNDO OFFSHORE E BOTÃO VOLTAR)
# =================================================================
elif st.session_state.pagina == "login":
    # CSS: Mesma imagem de fundo da Home (Offshore Petrolífera)
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
        /* Ajuste dos botões da tela de login */
        div.stButton > button {
            width: 100% !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
    
    # Centralização do formulário de login
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    
    with col_l2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        navio_sel = st.selectbox("Selecione sua Embarcação", list(USUARIOS.keys()))
        senha_dig = st.text_input("Senha de Acesso", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão Entrar
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
        
        # Botão Voltar
        if st.button("⬅️ VOLTAR AO INÍCIO"):
            st.session_state.pagina = "home"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
# =================================================================
# BLOCO 5: TELA DE MENU PRINCIPAL (COM SAUDAÇÃO)
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    
    # Mensagem de Boas-vindas Personalizada
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

# =================================================================
# BLOCO 6: CONFERÊNCIA DE ESTOQUE - COM BOTÕES DE EXPORTAÇÃO
# =================================================================
elif st.session_state.pagina == "lista":
    import io
    from datetime import datetime, timedelta
    import unicodedata

    # 1. ESTILO VISUAL E FUNDO
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                        url("https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        /* Botões de Exportação Brancos */
        .btn-export {
            background-color: white !important; color: #004aad !important;
            border-radius: 10px !important; font-weight: bold !important;
            border: 1px solid #004aad !important;
        }
        /* Botões de Ação Azuis */
        div.stButton > button {
            background-color: #004aad !important; color: white !important;
            border-radius: 20px !important; font-weight: bold !important;
        }
        .stDataFrame { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        h1, h2, h3, p, label { color: white !important; text-shadow: 2px 2px 5px black; }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    
    # 2. BOTÃO DE ATUALIZAR (CORRIGIDO)
    col_refresh, col_spacer = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 ATUALIZAR TABELA", use_container_width=True):
            st.session_state.df_lista = carregar_dados_do_notion()
            st.toast("Dados sincronizados!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. CONFIGURAÇÃO DA TABELA E SEGURANÇA
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

    # Verificação de limite para trava de segurança
    itens_excedentes = df_editado[df_editado["CONFIRMA"] > df_editado["PREDEFINIDO"]]
    if not itens_excedentes.empty:
        pode_exportar = False
        st.error("⚠️ BLOQUEIO: VALOR ACIMA DO LIMITE PERMITIDO!")

    st.markdown("---")
    
    # 4. BOTÕES DE EXPORTAÇÃO E NAVEGAÇÃO
    col_pdf, col_excel, col_menu = st.columns(3)
    
    with col_pdf:
        if pode_exportar:
            try:
                def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')
                
                class PDF_Checklist(FPDF):
                    def header(self):
                        # Logo e Cabeçalho idêntico ao padrão tratado
                        if os.path.exists("ZION.jpg"): self.image("ZION.jpg", 95, 8, 20)
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
                        # Horário de Brasília
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
# BLOCO 7: TELA DE DECLARAÇÃO (RESTAURADA E CONECTADA AO NOTION)
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

    # --- CSS PARA FUNDO AZUL E CONTRASTE ---
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

    # Navegação Superior
    c_nav1, c_nav2, c_nav3 = st.columns([1, 2, 1])
    with c_nav1:
        if st.button("⬅️ MENU", use_container_width=True):
            st.session_state.pagina = "menu"; st.rerun()
    with c_nav3:
        if st.button("🚪 SAIR", use_container_width=True):
            st.session_state.pagina = "login"; st.rerun()

    st.markdown("<h1 style='text-align: center;'>⚓ Declaração de Reabastecimento</h1>", unsafe_allow_html=True)
    
    # --- LOGICA DE ESCOLTA ---
    col_esc, col_val = st.columns([2, 2])
    with col_esc:
        escolta_opcoes = {"NÃO": 0, "SIM": 1}
        escolta_sel = st.radio("O navio está com escolta?", list(escolta_opcoes.keys()), horizontal=True)
        dias_duracao = 12 if escolta_sel == "SIM" else 15
    
    with col_val:
        data_recebimento = st.date_input("Data prevista para o novo rancho:", datetime.now(), format="DD/MM/YYYY")
        data_validade = data_recebimento + timedelta(days=dias_duracao)
        st.success(f"📅 Validade: {data_validade.strftime('%d/%m/%Y')} ({dias_duracao} dias)")

    with st.form("form_declaracao_completo"):
        c1, c2 = st.columns(2)
        with c1:
            resp_nome = st.text_input("Responsável", value=st.session_state.get('cozinheiro', 'CZA AUGUSTO'), disabled=True)
            navio_nome = st.text_input("Navio", value=st.session_state.get('navio', 'JATOBA'), disabled=True)
            origem = st.text_input("Porto de Origem", value="Porto Velho")
        with c2:
            qtde_trip = st.number_input("Qtde Tripulante:", min_value=1, value=16)
            data_ultimo = st.date_input("Data do último rancho:", format="DD/MM/YYYY")
            destino = st.text_input("Porto de Destino", value="Novo remanso")
        
        consideracoes = st.text_area("Considerações:", value="Consumo regular conforme escala.")
        
        st.write("Assinatura Digital:")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#FFFFFF",
            height=120, drawing_mode="freedraw", key="canvas_restaurado"
        )
        
        btn_acao = st.form_submit_button("💾 SALVAR E GERAR PDF ORIGINAL", use_container_width=True)

    # --- LÓGICA DE SALVAMENTO E PDF ---
    if btn_acao:
        if canvas_result.image_data is not None:
            try:
                # 1. Gerar imagem da assinatura
                img_ass = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                buffered = BytesIO()
                img_ass.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # 2. Criar PDF (Sua lógica que já funciona)
                pdf = FPDF()
                pdf.add_page()
                def f(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')
                
                pdf.set_font("Arial", "B", 35); pdf.set_text_color(0, 51, 153); pdf.cell(0, 20, "ZION", ln=True, align="C")
                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 14); pdf.cell(0, 10, f("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C"); pdf.ln(10)
                
                pdf.set_font("Arial", "", 12)
                corpo = (f"Pelo presente, certifico que a lotacao de tripulantes a bordo do empurrador {navio_nome} e de {qtde_trip} tripulantes. "
                         f"A provisao de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da tripulacao "
                         f"por um periodo de {dias_duracao} dias nauticos a partir de {data_recebimento.strftime('%d/%m/%Y')}. "
                         f"Este suprimento e planejado para a viagem corrente.\n\n"
                         f"Origem: {origem} | Destino: {destino}")
                pdf.multi_cell(0, 10, f(corpo))
                
                pdf.ln(35)
                agora_br = datetime.now(pytz.timezone('America/Sao_Paulo'))
                txt_hora = agora_br.strftime('%d/%m/%Y às %H:%M')

                img_ass.save("temp_sign.png")
                pdf.image("temp_sign.png", x=75, w=50)
                pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
                pdf.set_font("Arial", "B", 11); pdf.cell(0, 7, f(resp_nome), ln=True, align="C")
                pdf.set_font("Arial", "I", 9); pdf.cell(0, 5, f(f"Assinado em: {txt_hora}"), ln=True, align="C")

                # Botão de Download
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 BAIXAR PDF ORIGINAL", data=pdf_bytes, file_name=f"Declaracao_{navio_nome}.pdf", use_container_width=True)

                # 3. SALVAR NO NOTION (USANDO SUAS VARIÁVEIS DO BLOCO 1)
                headers_n = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
                payload_n = {
                    "parent": {"database_id": ID_HISTORICO_NOTION},
                    "properties": {
                        "Responsável": {"title": [{"text": {"content": resp_nome}}]},
                        "Navio": {"rich_text": [{"text": {"content": navio_nome}}]},
                        "Novo Rancho": {"date": {"start": data_recebimento.isoformat()}},
                        "Porto de Origem": {"rich_text": [{"text": {"content": origem}}]},
                        "Porto de Destino": {"rich_text": [{"text": {"content": destino}}]},
                        "Qtde Tripulante": {"number": int(qtde_trip)}
                    }
                }
                res_n = requests.post("https://api.notion.com/v1/pages", headers=headers_n, json=payload_n)
                if res_n.status_code == 200:
                    st.success("✅ Registro salvo no Notion!")
                else:
                    st.warning(f"PDF Gerado, mas erro ao salvar no Notion: {res_n.status_code}")

            except Exception as e:
                st.error(f"Erro ao processar: {e}")
# =================================================================
# BLOCO 8: HISTÓRICO E 2ª VIA - MODELO FINAL ZION
# =================================================================
elif st.session_state.pagina == "historico":
    import requests
    from datetime import date, datetime
    import unicodedata
    from fpdf import FPDF
    import base64
    from io import BytesIO
    from PIL import Image

    st.markdown("""
        <style>
        .stApp { background-color: #3b66eb !important; }
        h1, h2, p, label, .stMarkdown { color: #ffffff !important; }
        div[data-testid="stExpander"] { background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 10px; }
        div.stButton > button { border-radius: 8px; border: 2px solid #ffffff; background-color: transparent; color: #ffffff; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    if st.button("⬅️ MENU PRINCIPAL"):
        st.session_state.pagina = "menu"; st.rerun()

    st.markdown("<h2 style='text-align: center;'>🗄️ Histórico de Documentos</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 2, 1])
    d_ini = c1.date_input("De:", value=date(2025, 12, 15))
    d_fim = c2.date_input("Até:", value=date.today())
    
    if c3.button("🔍 CONSULTAR"):
        headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
        filtro = {"property": "Novo Rancho", "date": {"on_or_after": d_ini.isoformat(), "on_or_before": d_fim.isoformat()}}
        res = requests.post(f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query", headers=headers, json={"filter": filtro})
        
        if res.status_code == 200:
            results = res.json().get("results", [])
            dados = []
            for page in results:
                p = page.get("properties", {})
                
                # Funções de extração segura para evitar erros de tela
                def g_t(n): return p.get(n, {}).get("rich_text", [{}])[0].get("plain_text", "N/A") if p.get(n) and p.get(n).get("rich_text") else "N/A"
                def g_tit(n): return p.get(n, {}).get("title", [{}])[0].get("plain_text", "N/A") if p.get(n) and p.get(n).get("title") else "N/A"
                def g_dt(n): return p.get(n, {}).get("date", {}).get("start", "S/D") if p.get(n) and p.get(n).get("date") else "S/D"
                def g_num(n): return p.get(n, {}).get("number", 0) if p.get(n) else 0

                dados.append({
                    "navio": g_t("Navio"),
                    "data": g_dt("Novo Rancho"),
                    "resp": g_tit("Responsável"),
                    "origem": g_t("Porto de Origem"),
                    "destino": g_t("Porto de Destino"),
                    "tripulantes": g_num("Qtde Tripulante"),
                    "consideracoes": g_t("Considerações"),
                    "assinatura_base64": g_t("Assinatura") # Pega a string base64 salva
                })
            st.session_state.dados_busca = dados
            st.rerun()

    if st.session_state.get("dados_busca"):
        for idx, r in enumerate(st.session_state.dados_busca):
            with st.expander(f"🚢 {r['navio']} | 📅 {r['data']} | 👤 {r['resp']}"):
                if st.button(f"📄 GERAR PDF (2ª VIA)", key=f"b_{idx}"):
                    pdf = FPDF()
                    pdf.add_page()
                    def f(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')
                    
                    # --- CABEÇALHO ZION ---
                    pdf.set_font("Arial", "B", 35); pdf.set_text_color(0, 51, 153)
                    pdf.cell(0, 25, "ZION", ln=True, align="C")
                    
                    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, f("DECLARACAO DE REABASTECIMENTO"), ln=True, align="C"); pdf.ln(15)
                    
                    # --- CORPO DO TEXTO (CONFORME SOLICITADO) ---
                    pdf.set_font("Arial", "", 12)
                    dt_f = datetime.strptime(r['data'], '%Y-%m-%d').strftime('%d/%m/%Y') if r['data'] != "S/D" else r['data']
                    
                    texto_corpo = (
                        f"Pelo presente, certifico que a lotacao de tripulantes a bordo do empurrador {r['navio']} e de {r['tripulantes']} "
                        f"tripulantes. A provisao de rancho a ser reabastecida destina-se a cobrir as necessidades "
                        f"nutricionais da tripulacao por um periodo de 15 dias nauticos a partir de {dt_f}. Este "
                        f"suprimento e planejado para a viagem corrente.\n\n"
                        f"Origem: {r['origem']} | Destino: {r['destino']}"
                    )
                    pdf.multi_cell(0, 10, f(texto_corpo))
                    
                    if r['consideracoes'] != "N/A" and r['consideracoes'].strip() != "":
                        pdf.ln(5); pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, "Consideracoes:", ln=True)
                        pdf.set_font("Arial", "", 12); pdf.multi_cell(0, 8, f(r['consideracoes']))

                    # --- ASSINATURA E RODAPÉ ---
                    pdf.ln(20)
                    
                    # Tenta carregar a assinatura se houver base64
                    if r['assinatura_base64'] != "N/A" and len(r['assinatura_base64']) > 100:
                        try:
                            # Limpa o prefixo se existir
                            base64_data = r['assinatura_base64'].split(",")[-1]
                            img_data = base64.b64decode(base64_data)
                            img_file = BytesIO(img_data)
                            pdf.image(img_file, x=80, w=50) # Assinatura acima da linha
                        except: pass

                    # Linha e Nome (Aproximados)
                    pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
                    pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 7, f(r['resp']), ln=True, align="C")
                    
                    # Data e Hora do Registro
                    pdf.set_font("Arial", "I", 9)
                    pdf.cell(0, 5, f(f"Assinado em: {dt_f} as {datetime.now().strftime('%H:%M')}"), ln=True, align="C")
                    
                    # Saída do PDF
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    st.download_button("⬇️ BAIXAR PDF", data=pdf_output, file_name=f"2via_{r['navio']}.pdf", key=f"dl_{idx}")
