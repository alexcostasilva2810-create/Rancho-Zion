import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests

# =================================================================
# BLOCO 1: CONFIGURAÇÕES INICIAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Definição das colunas ANTES de qualquer uso (Evita o erro da imagem c56e2c.png)
COLUNAS_PADRAO = ["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"]

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state:
    st.session_state.cozinheiro = ""
if 'navio' not in st.session_state:
    st.session_state.navio = ""
if 'pdf_disponivel' not in st.session_state:
    st.session_state.pdf_disponivel = None
if 'df_lista' not in st.session_state:
    st.session_state.df_lista = pd.DataFrame(columns=COLUNAS_PADRAO)

USUARIOS = {
    "NAVIO 01": {"nome": "João", "senha": "123"},
    "AROEIRA": {"nome": "Marcos", "senha": "789"},
    "NAVIO 03": {"nome": "Carlos", "senha": "456"}
}

# =================================================================
# BLOCO 2: CONEXÃO COM NOTION
# =================================================================
def carregar_dados_do_notion():
    NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
    DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1"
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
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
            df['ITEM'] = pd.to_numeric(df['ITEM'], errors='coerce')
            return df.sort_values(by='ITEM').reset_index(drop=True)
        return st.session_state.df_lista
    except:
        return st.session_state.df_lista

# =================================================================
# BLOCO 3: ESTILO PADRÃO (AZUL) PARA AS OUTRAS TELAS
# =================================================================
def aplicar_estilo_azul():
    st.markdown("""
        <style>
        .stApp { background-color: #4169E1 !important; background-image: none !important; }
        h1, h2, h3, p, label { color: white !important; }
        div.stButton > button { background-color: #FF8C00 !important; color: black !important; font-weight: 900 !important; border-radius: 10px !important; }
        </style>
        """, unsafe_allow_html=True)

# =================================================================
# BLOCO 4: NAVEGAÇÃO E TELAS
# =================================================================

if st.session_state.pagina == "home":
    aplicar_estilo_azul()
    st.markdown("<h1 style='text-align: center;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"):
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "login":
    aplicar_estilo_azul()
    st.title("🔐 Login")
    navio_sel = st.selectbox("Navio", list(USUARIOS.keys()))
    senha_dig = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        dados = USUARIOS.get(navio_sel)
        if dados and senha_dig == dados["senha"]:
            st.session_state.cozinheiro = dados["nome"]; st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.error("❌ Senha incorreta!")


# --- BLOCO 6: TELA DE LISTA (CONFERÊNCIA DE ESTOQUE) ---
elif st.session_state.pagina == "lista":
    # CSS: Fundo de estoque e botões nítidos
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        div.stButton > button {
            background-color: #FF8C00 !important;
            color: white !important;
            border: 1px solid #FF8C00 !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 2px black !important;
        }
        h1, h2, h3, p, label { color: white !important; text-shadow: 2px 2px 4px black; }
        .stDataFrame { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📋 Conferência de Estoque")
    
    if st.button("🔄 ATUALIZAR DADOS DO NOTION"):
        st.session_state.df_lista = carregar_dados_do_notion()
        st.rerun()

    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("CÓD.", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("SUA QTD", min_value=0),
        },
        hide_index=True, use_container_width=True, key="editor_estoque_final"
    )

    st.markdown("---")
    col_pdf, col_voltar = st.columns(2)
    
    with col_pdf:
        def preparar_celula(conteudo):
            texto = str(conteudo) if conteudo is not None else ""
            texto = texto.replace('\u2013', '-').replace('\u2014', '-')
            return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

        try:
            from datetime import timedelta

            class PDF(FPDF):
                def footer(self):
                    self.set_y(-15)
                    self.set_font('Arial', 'I', 8)
                    # AJUSTE DE HORÁRIO: UTC-3 (Brasília)
                    agora_brasilia = datetime.now() - timedelta(hours=3)
                    data_hora = agora_brasilia.strftime("%d/%m/%Y %H:%M:%S")
                    self.cell(0, 10, f'Gerado em: {data_hora} - Pagina ' + str(self.page_no()), 0, 0, 'C')

            # Orientação Retrato (P)
            pdf = PDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            
            # Logo Centralizada
            if os.path.exists("ZION.jpg"):
                pdf.image("ZION.jpg", 95, 8, 20) 
            
            # Cabeçalho Centralizado
            pdf.set_font("Arial", "B", 14)
            pdf.set_y(30)
            pdf.cell(0, 10, preparar_celula(f"Checklist de Rancho: {st.session_state.navio}"), ln=True, align="C")
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, preparar_celula(f"Responsavel: {st.session_state.cozinheiro}"), ln=True, align="C")
            pdf.ln(5)
            
            # Tabela (Larguras ajustadas para Retrato)
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(220, 220, 220)
            larguras = [10, 55, 25, 15, 20, 50, 15] 
            titulos = ["COD", "ITEM", "TIPO", "UNID", "PREDEF", "DESCRICAO", "CONF."]
            
            for i, t in enumerate(titulos):
                pdf.cell(larguras[i], 10, t, 1, 0, "C", True)
            pdf.ln()

            pdf.set_font("Arial", "", 7)
            for _, row in df_editado.iterrows():
                pdf.cell(larguras[0], 8, preparar_celula(row.get("ITEM", "")), 1, 0, "C")
                pdf.cell(larguras[1], 8, preparar_celula(row.get("ITEM", "")), 1) 
                pdf.cell(larguras[2], 8, preparar_celula(row.get("TIPO", "")), 1)
                pdf.cell(larguras[3], 8, preparar_celula(row.get("UNID MED", "")), 1, 0, "C")
                pdf.cell(larguras[4], 8, preparar_celula(row.get("PREDEFINIDO", "0")), 1, 0, "C")
                pdf.cell(larguras[5], 8, preparar_celula(row.get("DESCRIÇÃO", "")), 1)
                pdf.cell(larguras[6], 8, preparar_celula(row.get("CONFIRMA", "0")), 1, 1, "C")

            pdf_output = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="📥 BAIXAR PDF DO ESTOQUE",
                data=pdf_output,
                file_name=f"Rancho_{st.session_state.navio}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao preparar PDF: {e}")

    with col_voltar:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"
            st.rerun()

# --- BLOCO 7: TELA DE DECLARAÇÃO / TRIPULAÇÃO ---
elif st.session_state.pagina == "tripulacao":
    from datetime import datetime, timedelta
    
    # CSS: Fundo de alto mar e centralização do cabeçalho
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                        url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920");
            background-size: cover; background-position: center;
        }
        /* Centraliza o Título e o Ícone */
        .titulo-centralizado {
            text-align: center;
            color: white;
            text-shadow: 2px 2px 4px black;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 20px;
        }
        div.stButton > button {
            background-color: #FF8C00 !important;
            color: white !important;
            border: 1px solid #FF8C00 !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 2px black !important;
        }
        h3, p, label { color: white !important; text-shadow: 2px 2px 4px black; }
        .stTextInput>div>div>input, .stTextArea textarea, .stNumberInput input { 
            background-color: rgba(255, 255, 255, 0.9) !important; 
        }
        </style>
        """, unsafe_allow_html=True)

    # Cabeçalho Centralizado com Ícone de Âncora
    st.markdown("<div class='titulo-centralizado'>⚓ Declaração de Reabastecimento</div>", unsafe_allow_html=True)
    
    # --- LÓGICA DE ALERTAS E CÁLCULOS ---
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
            # Responsável preenchido com o nome do login
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
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3, stroke_color="#000000",
            background_color="#FFFFFF",
            height=120, drawing_mode="freedraw", key="ass_final_ancora",
        )
        
        enviar = st.form_submit_button("💾 SALVAR E GERAR PDF OFICIAL")

    if enviar:
        if canvas_result.image_data is None:
            st.error("❌ Realize a assinatura antes de gerar o PDF.")
        else:
            try:
                import unicodedata
                from fpdf import FPDF
                from PIL import Image

                class PDF_Final(FPDF):
                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Arial', 'I', 8)
                        agora_br = datetime.now() - timedelta(hours=3)
                        self.cell(0, 10, f'Gerado em: {agora_br.strftime("%d/%m/%Y %H:%M:%S")} - Pagina ' + str(self.page_no()), 0, 0, 'C')

                pdf = PDF_Final(orientation='P', unit='mm', format='A4')
                pdf.add_page()

                def preparar(t):
                    return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
                pdf.set_font("Arial", "B", 16)
                pdf.set_y(30)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, preparar(f"Embarcação: {st.session_state.navio}"), ln=True, align="C")
                pdf.ln(10)

                # Conteúdo do documento
                pdf.set_font("Arial", "", 12)
                texto_corpo = (
                    f"Pelo presente, certifico que a lotação de tripulantes a bordo do empurrador é de {lotacao} tripulantes. "
                    f"A provisão de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da tripulação "
                    f"por um período de {dias_duracao} dias náuticos a partir de {data_recebimento.strftime('%d/%m/%Y')}. "
                    f"Este suprimento é planejado para a viagem corrente."
                )
                pdf.multi_cell(0, 8, preparar(texto_corpo), align="J")
                pdf.ln(5)

                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, preparar(f"Origem: {origem} | Destino: {destino}"), ln=True)
                pdf.cell(0, 8, preparar(f"Último Rancho: {data_ultimo_rancho.strftime('%d/%m/%Y')}"), ln=True)
                
                if necessidades_extras:
                    pdf.ln(5)
                    pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, preparar("CONSIDERAÇÕES:"), ln=True)
                    pdf.set_font("Arial", "", 10); pdf.multi_cell(0, 7, preparar(necessidades_extras), align="J")
                
                # Área de Assinatura
                img_ass = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_ass.save("temp_ass.png")
                pdf.ln(15)
                pdf.cell(0, 10, preparar("__________________________________________"), ln=True, align="C")
                pdf.image("temp_ass.png", x=75, y=pdf.get_y()-17, w=60)
                pdf.cell(0, 10, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True, align="C")

                st.download_button(label="📥 BAIXAR DECLARAÇÃO (PDF)", data=pdf.output(dest='S').encode('latin-1'), 
                                   file_name=f"Declaracao_{st.session_state.navio}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"; st.rerun()

# --- BLOCO 8: MÓDULO DE AUDITORIA E HISTÓRICO ---
elif st.session_state.pagina == "historico":
    import pandas as pd
    import requests

    st.markdown("<h1 style='text-align: center; color: white;'>📜 Auditoria e Histórico</h1>", unsafe_allow_html=True)
    
    # Recupera o ID que definimos no menu
    ID_DOC = st.session_state.id_historico 

    try:
        url = f"https://api.notion.com/v1/databases/{ID_DOC}/query"
        
        # Filtro de segurança: Cozinheiro só vê o navio atual, Admin vê tudo
        if st.session_state.cozinheiro.lower() == "admin":
            payload = {"sorts": [{"property": "Data Pedido", "direction": "descending"}]}
        else:
            payload = {
                "filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}},
                "sorts": [{"property": "Data Pedido", "direction": "descending"}]
            }

        res = requests.post(url, headers=headers, json=payload)
        
        if res.status_code == 200:
            dados = res.json().get("results", [])
            tab_final = []
            for item in dados:
                p = item["properties"]
                tab_final.append({
                    "Data": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "-",
                    "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                    "Navio": p["Navio"]["rich_text"][0]["text"]["content"] if p["Navio"]["rich_text"] else "N/A",
                    "Validade": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "-"
                })
            
            df = pd.DataFrame(tab_final)
            
            # Se você for Admin, aparece o filtro de pesquisa por cozinheiro
            if st.session_state.cozinheiro.lower() == "admin" and not df.empty:
                lista_users = sorted(df["Cozinheiro"].unique().tolist())
                busca = st.selectbox("Pesquisar Cozinheiro:", ["TODOS"] + lista_users)
                if busca != "TODOS":
                    df = df[df["Cozinheiro"] == busca]

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error(f"Erro de conexão com o Notion: {res.status_code}")

    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")

    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state.pagina = "menu"
        st.rerun()
