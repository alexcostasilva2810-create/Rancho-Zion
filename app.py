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
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
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
# BLOCO 7: RESTAURAÇÃO DA TELA ORIGINAL (ESTÁVEL)
# =================================================================
elif st.session_state.pagina == "gerar_declaracao":
    import requests
    from fpdf import FPDF
    from datetime import datetime, timedelta

    # Estilo original
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        h1, h2, h3 { color: #0D47A1 !important; }
        div.stButton > button {
            background-color: #0D47A1 !important;
            color: white !important;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📄 Gerar Declaração")

    # Recuperação dos dados das telas anteriores
    navio = st.session_state.get('navio', 'Não selecionado')
    data_pedido = st.session_state.get('data_rancho', datetime.now().date())
    usuario = st.session_state.get('usuario', 'Zion User')
    escolta = st.session_state.get('escolta', False)

    st.subheader("Resumo do Pedido")
    st.write(f"**Navio:** {navio}")
    st.write(f"**Data:** {data_pedido.strftime('%d/%m/%Y')}")
    st.write(f"**Responsável:** {usuario}")

    st.markdown("---")

    # Função de salvamento com os nomes atuais do seu Notion (Imagem 15/17)
    def salvar_no_banco():
        try:
            url = "https://api.notion.com/v1/pages"
            headers = {
                "Authorization": f"Bearer {st.secrets['notion_token']}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            payload = {
                "parent": {"database_id": st.secrets["database_id"]},
                "properties": {
                    "RESPONSÁVEL": {"title": [{"text": {"content": usuario}}]},
                    "Navio": {"select": {"name": navio}},
                    "Data prevista para rece...": {"date": {"start": data_pedido.isoformat()}},
                    "Validade": {"date": {"start": (data_pedido + timedelta(days=15)).isoformat()}},
                    "O navio está com escolt...": {"checkbox": escolta}
                }
            }
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except:
            return False

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 FINALIZAR E SALVAR", use_container_width=True):
            if salvar_no_banco():
                st.success("✅ Gravado com sucesso no Histórico!")
                
                # Geração simples de PDF (Original)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "DECLARAÇÃO DE RANCHO", ln=True, align='C')
                pdf_output = pdf.output(dest='S').encode('latin-1')
                
                st.download_button(
                    label="📥 BAIXAR PDF",
                    data=pdf_output,
                    file_name=f"Declaracao_{navio}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("Erro ao salvar. Verifique a conexão com o Notion.")

    with col2:
        if st.button("⬅️ VOLTAR", use_container_width=True):
            st.session_state.pagina = "lista"
            st.rerun()

    if st.button("🏠 MENU PRINCIPAL", use_container_width=True):
        st.session_state.pagina = "menu"
        st.rerun()
# =================================================================
# BLOCO 8: HISTÓRICO - CONEXÃO INTEGRAL COM NOTION (AJUSTADO)
# =================================================================
elif st.session_state.pagina == "historico":
    import requests
    from datetime import date

    # --- 1. FUNÇÃO DE BUSCA (Ajustada para os nomes da Imagem 15) ---
    def carregar_historico_notion(dt_inicio, dt_fim):
        try:
            NOTION_TOKEN = st.secrets["notion_token"]
            DATABASE_ID = st.secrets["database_id"]
            
            url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            headers = {
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            
            # Filtro pela coluna "Data prevista para rece..."
            query = {
                "filter": {
                    "and": [
                        {"property": "Data prevista para rece...", "date": {"on_or_after": dt_inicio.isoformat()}},
                        {"property": "Data prevista para rece...", "date": {"on_or_before": dt_fim.isoformat()}}
                    ]
                }
            }
            
            response = requests.post(url, json=query, headers=headers)
            if response.status_code == 200:
                results = response.json().get("results", [])
                lista_final = []
                for item in results:
                    p = item["properties"]
                    # Mapeamento conforme Imagem 15
                    lista_final.append({
                        "usuario": p["RESPONSÁVEL"]["title"][0]["text"]["content"] if p["RESPONSÁVEL"]["title"] else "N/A",
                        "empurrador": p["Navio"]["select"]["name"] if p["Navio"]["select"] else "N/A",
                        "data_receb": p["Data prevista para rece..."]["date"]["start"] if p["Data prevista para rece..."]["date"] else "-",
                        "validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-",
                        "escolta": "SIM" if p["O navio está com escolt..."]["checkbox"] else "NÃO"
                    })
                return lista_final
            else:
                st.error(f"Erro Notion: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            return []

    # --- 2. LAYOUT E ESTILO ---
    st.markdown("""
        <style>
        .stApp { background-color: #F0F8FF !important; }
        h1, h2, label { color: #0D47A1 !important; font-weight: bold; }
        div.stButton > button { background-color: #0D47A1 !important; color: white !important; border-radius: 8px !important; }
        </style>
        """, unsafe_allow_html=True)

    st.title("🗄️ Banco de Dados - Histórico")

    # --- 3. FILTROS ---
    c1, c2, c3 = st.columns([2, 2, 1])
    # Usei 'data_inicio' e 'data_fim' para evitar o erro da imagem 14
    data_inicio = c1.date_input("🗓️ Data Início", value=date.today(), format="DD/MM/YYYY")
    data_fim = c2.date_input("🗓️ Data Fim", value=date.today(), format="DD/MM/YYYY")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if c3.button("🔍 BUSCAR"):
        with st.spinner("Buscando dados..."):
            st.session_state.historico_declaracoes = carregar_historico_notion(data_inicio, data_fim)
        st.rerun()

    st.markdown("---")

    # --- 4. TABELA DE RESULTADOS ---
    cols_h = st.columns([1.5, 1.5, 1.2, 1.2, 0.8, 1])
    titulos = ["USUÁRIO", "EMPURRADOR", "DATA RECEB.", "VALIDADE", "ESCOLTA", "IMPRIMIR"]
    for i, t in enumerate(titulos):
        cols_h[i].markdown(f"**{t}**")
    st.markdown("<hr style='border-top: 2px solid #0D47A1;'>", unsafe_allow_html=True)

    if "historico_declaracoes" not in st.session_state or not st.session_state.historico_declaracoes:
        st.info("Nenhum registro encontrado para este período.")
    else:
        for idx, reg in enumerate(st.session_state.historico_declaracoes):
            r = st.columns([1.5, 1.5, 1.2, 1.2, 0.8, 1])
            r[0].write(reg["usuario"])
            r[1].write(reg["empurrador"])
            r[2].write(reg["data_receb"])
            r[3].write(reg["validade"])
            r[4].write(reg["escolta"])
            with r[5]:
                st.button("🖨️ 2ª VIA", key=f"btn_{idx}")
            st.markdown("<hr style='margin:0; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)

    # --- 5. NAVEGAÇÃO ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("⬅️ VOLTAR AO MENU PRINCIPAL", use_container_width=True):
            st.session_state.pagina = "menu"; st.rerun()
    with col_v2:
        if st.button("🚪 SAIR DO SISTEMA", use_container_width=True):
            st.session_state.pagina = "home"; st.rerun()
