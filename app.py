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
        st.rerun()# =================================================================
# BLOCO 6: TELA DE LISTA (AJUSTE DE HORÁRIO E CLARIDADE)
# =================================================================
elif st.session_state.pagina == "lista":
    import io
    from datetime import datetime, timedelta
    
    # 1. PLANO DE FUNDO MAIS SUAVE (OPACIDADE REDUZIDA)
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                        url("https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=1920");
            background-size: cover; background-position: center; background-attachment: fixed;
        }
        div.stButton > button {
            background-color: #FF8C00 !important; color: white !important;
            border-radius: 10px !important; font-weight: bold !important;
            text-shadow: 1px 1px 2px black !important;
        }
        .stDataFrame { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        h1, h2, h3, p, label { color: white !important; text-shadow: 2px 2px 5px black; }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    
    # Lógica de Dados e Tabela (Mantida conforme solicitado)
    pode_exportar = True 
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("COD", disabled=True),
            "PREDEFINIDO": st.column_config.NumberColumn("LIMITE", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("NECESSIDADE", min_value=0),
        },
        hide_index=True, use_container_width=True, key="editor_estoque_v6"
    )

    # Verificação de Limite
    itens_excedentes = df_editado[df_editado["CONFIRMA"] > df_editado["PREDEFINIDO"]]
    if not itens_excedentes.empty:
        pode_exportar = False
        st.error("⚠️ BLOQUEIO: VALOR ACIMA DO LIMITE PERMITIDO!")

    st.markdown("---")
    col_pdf, col_excel, col_voltar = st.columns(3)
    
    with col_pdf:
        if pode_exportar:
            try:
                def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

                class PDF_Checklist(FPDF):
                    def header(self):
                        if os.path.exists("ZION.jpg"): self.image("ZION.jpg", 95, 8, 20)
                        self.set_font("Arial", "B", 14)
                        self.ln(22)
                        self.cell(0, 10, preparar(f"Checklist de Rancho: {st.session_state.navio}"), ln=True, align="C")
                        self.ln(5)
                        self.set_fill_color(200, 200, 200)
                        self.set_font("Arial", "B", 8)
                        self.cell(10, 7, "COD", 1, 0, "C", True)
                        self.cell(30, 7, "TIPO", 1, 0, "C", True)
                        self.cell(15, 7, "UNID", 1, 0, "C", True)
                        self.cell(15, 7, "PREDEF", 1, 0, "C", True)
                        self.cell(105, 7, "DESCRICAO", 1, 0, "C", True)
                        self.cell(15, 7, "CONF.", 1, 1, "C", True)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Arial', 'I', 8)
                        # --- AJUSTE PARA HORÁRIO DE BRASÍLIA (UTC-3) ---
                        fuso_brasilia = datetime.now() - timedelta(hours=3)
                        data_hora = fuso_brasilia.strftime("%d/%m/%Y %H:%M:%S")
                        texto_rodape = f"Gerado em: {data_hora} (Horário de Brasília) - Pagina {self.page_no()}"
                        self.cell(0, 10, preparar(texto_rodape), 0, 0, 'C')

                pdf = PDF_Checklist()
                pdf.add_page()
                pdf.set_font("Arial", "", 8)

                for _, r in df_editado.iterrows():
                    pdf.cell(10, 6, str(r["ITEM"]), 1, 0, "C")
                    pdf.cell(30, 6, preparar(r["TIPO"]), 1, 0, "L")
                    pdf.cell(15, 6, preparar(r["UNID MED"]), 1, 0, "C")
                    pdf.cell(15, 6, str(r["PREDEFINIDO"]), 1, 0, "C")
                    pdf.cell(105, 6, preparar(r["DESCRIÇÃO"]), 1, 0, "L")
                    pdf.cell(15, 6, str(r["CONFIRMA"]), 1, 1, "C")

                st.download_button(
                    label="📥 BAIXAR PDF", 
                    data=pdf.output(dest='S').encode('latin-1'), 
                    file_name=f"Checklist_{st.session_state.navio}.pdf", 
                    mime="application/pdf", 
                    use_container_width=True
                )
            except Exception as e: st.error(f"Erro no PDF: {e}")

    # (Botão de Excel e Voltar permanecem iguais ao anterior)
    with col_excel:
        if pode_exportar:
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_editado.to_excel(writer, index=False, sheet_name='Rancho')
                st.download_button(label="📊 BAIXAR EXCEL", data=buffer.getvalue(), file_name=f"Rancho_{st.session_state.navio}.xlsx", use_container_width=True)
            except: st.error("Erro no Excel.")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun() 
            
# =================================================================
# BLOCO 7: TELA DE DECLARAÇÃO / TRIPULAÇÃO
# =================================================================
elif st.session_state.pagina == "tripulacao":
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                        url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        .titulo-centralizado {
            text-align: center; color: white; text-shadow: 2px 2px 4px black;
            font-size: 2.5rem; font-weight: bold; margin-bottom: 20px;
        }
        div.stButton > button {
            background-color: #FF8C00 !important; color: white !important;
            border: 1px solid #FF8C00 !important; font-weight: bold !important;
            text-shadow: 1px 1px 2px black !important;
        }
        h3, p, label { color: white !important; text-shadow: 2px 2px 4px black; }
        .stTextInput>div>div>input, .stTextArea textarea, .stNumberInput input { 
            background-color: rgba(255, 255, 255, 0.9) !important; 
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<div class='titulo-centralizado'>⚓ Declaração de Reabastecimento</div>", unsafe_allow_html=True)
    
    escolta = st.radio("O navio está com escolta?", ["NÃO", "SIM"], horizontal=True)
    dias_duracao = 12 if escolta == "SIM" else 15
    col_datas1, col_datas2 = st.columns(2)
    with col_datas1:
        data_recebimento = st.date_input("Data prevista para receber o novo rancho:", datetime.now(), format="DD/MM/YYYY")
    
    data_validade = data_recebimento + timedelta(days=dias_duracao)
    with col_datas2:
        st.markdown(f"### 📅 Validade do Rancho")
        cor_alerta = "#FF8C00" if escolta == "SIM" else "#00FF00"
        st.markdown(f"<div style='background-color:{cor_alerta}; padding:10px; border-radius:5px; color:black; font-weight:bold; text-align:center;'>"
                    f"Com {dias_duracao} dias, seu rancho durará até: {data_validade.strftime('%d/%m/%Y')}"
                    f"</div>", unsafe_allow_html=True)

    with st.form("form_declaracao_final"):
        col1, col2 = st.columns(2)
        with col1:
            resp_nome = st.text_input("Responsável (Login)", value=st.session_state.cozinheiro, disabled=True)
            lotacao = st.number_input("Número de tripulantes a bordo:", min_value=1, value=16)
            origem = st.text_input("Porto de Origem", value="Porto Velho")
        with col2:
            data_ultimo_rancho = st.date_input("Data do último rancho recebido:", format="DD/MM/YYYY")
            destino = st.text_input("Porto de Destino", value="Novo remanso")
        
        necessidades_extras = st.text_area("Considerações / Necessidades Extras:", 
            value="Foi acrescentado 10 água no rancho pelo fato da baixa do rio. Por gentileza colocar 06 vassoura, 06 rodo, 02 pá de lixo de ferro...")
        
        st.write("Assinatura Digital:")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)", stroke_width=3, stroke_color="#000000",
            background_color="#FFFFFF", height=120, drawing_mode="freedraw", key="ass_final_ancora",
        )
        enviar = st.form_submit_button("💾 SALVAR E GERAR PDF OFICIAL")

    if enviar:
        if canvas_result.image_data is None:
            st.error("❌ Realize a assinatura antes de gerar o PDF.")
        else:
            try:
                class PDF_Final(FPDF):
                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Arial', 'I', 8)
                        agora_br = datetime.now() - timedelta(hours=3)
                        self.cell(0, 10, f'Gerado em: {agora_br.strftime("%d/%m/%Y %H:%M:%S")} - Pagina ' + str(self.page_no()), 0, 0, 'C')

                pdf = PDF_Final(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
                pdf.set_font("Arial", "B", 16); pdf.set_y(30)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.set_font("Arial", "B", 12); pdf.cell(0, 8, preparar(f"Embarcação: {st.session_state.navio}"), ln=True, align="C")
                pdf.ln(10)

                texto_corpo = (f"Pelo presente, certifico que a lotação de tripulantes a bordo do empurrador é de {lotacao} tripulantes. "
                               f"A provisão de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da tripulação "
                               f"por um período de {dias_duracao} dias náuticos a partir de {data_recebimento.strftime('%d/%m/%Y')}. "
                               f"Este suprimento é planejado para a viagem corrente.")
                pdf.set_font("Arial", "", 12); pdf.multi_cell(0, 8, preparar(texto_corpo), align="J")
                pdf.ln(5); pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, preparar(f"Origem: {origem} | Destino: {destino}"), ln=True)
                pdf.cell(0, 8, preparar(f"Último Rancho: {data_ultimo_rancho.strftime('%d/%m/%Y')}"), ln=True)
                
                if necessidades_extras:
                    pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, preparar("CONSIDERAÇÕES:"), ln=True)
                    pdf.set_font("Arial", "", 10); pdf.multi_cell(0, 7, preparar(necessidades_extras), align="J")
                
                img_ass = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_ass.save("temp_ass.png")
                pdf.ln(15); pdf.cell(0, 10, preparar("__________________________________________"), ln=True, align="C")
                pdf.image("temp_ass.png", x=75, y=pdf.get_y()-17, w=60)
                pdf.cell(0, 10, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True, align="C")

                st.download_button(label="📥 BAIXAR DECLARAÇÃO (PDF)", data=pdf.output(dest='S').encode('latin-1'), 
                                   file_name=f"Declaracao_{st.session_state.navio}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e: st.error(f"Erro: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 8: TELA DE HISTÓRICO DE DECLARAÇÕES
# =================================================================
elif st.session_state.pagina == "historico":
    # Estilo visual padronizado com o sistema
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                        url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        .stTable { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        h1, h2, th, td { color: white !important; text-shadow: 1px 1px 2px black; }
        </style>
        """, unsafe_allow_html=True)

    st.title(f"📜 Histórico de Declarações - {st.session_state.navio}")

    # Verifica se existem dados salvos no histórico (deve ser alimentado no Bloco 7)
    if "historico_declaracoes" not in st.session_state or not st.session_state.historico_declaracoes:
        st.warning("Nenhum registro de declaração encontrado para este período.")
    else:
        # Criando a tabela de exibição
        for idx, reg in enumerate(reversed(st.session_state.historico_declaracoes)):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
                
                # Exibição dos dados na mesma linha conforme solicitado
                col1.write(f"**Data Registro:** \n {reg['data_registro']}")
                col2.write(f"**Último Rancho:** \n {reg['ultimo_rancho']}")
                col3.write(f"**Origem:** \n {reg['origem']}")
                col4.write(f"**Destino:** \n {reg['destino']}")
                
                # Botão de retorno do arquivo PDF salvo
                with col5:
                    st.download_button(
                        label="📄 Ver PDF",
                        data=reg['pdf_binary'],
                        file_name=f"Declaracao_{reg['data_registro'].replace('/','_')}.pdf",
                        mime="application/pdf",
                        key=f"btn_hist_{idx}"
                    )
                st.markdown("---")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
