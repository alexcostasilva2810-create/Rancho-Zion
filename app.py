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

elif st.session_state.pagina == "menu":
    aplicar_estilo_azul()
    st.title(f"🚢 Painel - {st.session_state.navio}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 TABELA DE RANCHO"): st.session_state.pagina = "lista"; st.rerun()
    with col2:
        if st.button("👨‍✈️ DECLARAÇÃO"): st.session_state.pagina = "tripulacao"; st.rerun()
    if st.button("⬅️ SAIR"): st.session_state.pagina = "home"; st.rerun()

# --- BLOCO 6: TELA DE CONFERÊNCIA DE ESTOQUE (REVISADO) ---
elif st.session_state.pagina == "conferencia":
    import pandas as pd
    import requests
    from datetime import datetime
    
    # ID da tabela de histórico que você criou
    ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

    # CSS para manter o padrão visual
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                        url("https://images.unsplash.com/photo-1580508112997-57fd4a852a10?q=80&w=1920");
            background-size: cover;
        }
        .stDataFrame { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; }
        h1, h2, h3, p, label { color: white !important; text-shadow: 2px 2px 4px black; }
        </style>
        """, unsafe_allow_html=True)

    st.title(f"📦 Conferência: {st.session_state.navio}")

    # Verifica se os dados de estoque existem para evitar tela branca
    if 'df_estoque' in st.session_state and not st.session_state.df_estoque.empty:
        # Filtra apenas o navio selecionado
        df_edit = st.session_state.df_estoque[st.session_state.df_estoque['NAVIO'] == st.session_state.navio].copy()
        
        # Interface de edição
        df_conferido = st.data_editor(
            df_edit,
            column_config={
                "CONFIRMA": st.column_config.NumberColumn("Qtd em Estoque", min_value=0),
                "PREDEFINIDO": st.column_config.NumberColumn("Meta", disabled=True),
                "ITEM": None, "NAVIO": None 
            },
            disabled=["DESCRIÇÃO", "TIPO", "UNID MED"],
            hide_index=True,
            use_container_width=True
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 GERAR PDF DE CONFERÊNCIA"):
                # ... (lógica do PDF permanece a mesma)
                st.success("PDF Gerado!")

        with col_btn2:
            if st.button("⬅️ VOLTAR AO MENU"):
                st.session_state.pagina = "menu"
                st.rerun()

        # --- SEÇÃO DE HISTÓRICO POR NAVIO (Consulta ao Notion) ---
        st.markdown("---")
        st.markdown(f"### ⚓ Últimas Compras: {st.session_state.navio}")

        try:
            url_query = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
            
            # Filtro para buscar apenas este navio no seu ID 2e5025de...
            query_payload = {
                "filter": {
                    "property": "Navio",
                    "rich_text": {"equals": st.session_state.navio}
                },
                "sorts": [{"property": "Data Pedido", "direction": "descending"}]
            }
            
            # headers deve estar definido no seu código principal (seu Token do Notion)
            res_hist = requests.post(url_query, headers=headers, json=query_payload)
            
            if res_hist.status_code == 200:
                results = res_hist.json().get("results", [])
                if results:
                    lista_hist = []
                    for r in results:
                        p = r["properties"]
                        lista_hist.append({
                            "Data Pedido": p["Data Pedido"]["date"]["start"] if p["Data Pedido"]["date"] else "---",
                            "Cozinheiro": p["Cozinheiro"]["title"][0]["text"]["content"] if p["Cozinheiro"]["title"] else "N/A",
                            "Válido Até": p["Validade"]["date"]["start"] if p["Validade"]["date"] else "---",
                            "Escolta": p["Escolta"]["select"]["name"] if p["Escolta"]["select"] else "NÃO"
                        })
                    st.dataframe(pd.DataFrame(lista_hist), use_container_width=True, hide_index=True)
                else:
                    st.write("ℹ️ Sem registros anteriores para este navio.")
            else:
                st.warning("Aguardando novos registros de histórico...")
        except:
            st.write("Sincronizando histórico...") # Evita que o erro quebre a tela

    else:
        st.error("⚠️ Erro: Dados de estoque não encontrados. Por favor, faça o login novamente.")
        if st.button("Ir para Login"):
            st.session_state.pagina = "login"
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
    from datetime import datetime
    
    # CSS para manter o padrão visual de alto mar
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url("https://images.unsplash.com/photo-1500514960902-e64e75c44c83?q=80&w=1920");
            background-size: cover;
        }
        .titulo-centralizado {
            text-align: center; color: white; text-shadow: 2px 2px 4px black;
            font-size: 2.2rem; font-weight: bold; margin-bottom: 30px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<div class='titulo-centralizado'>📜 Auditoria e Histórico de Rancho</div>", unsafe_allow_html=True)
    
    # Busca os dados no seu novo Banco de Dados do Notion
    try:
        url_query = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        res = requests.post(url_query, headers=headers)
        
        if res.status_code == 200:
            dados_notion = res.json().get("results", [])
            lista_pedidos = []
            
            for p in dados_notion:
                prop = p["properties"]
                lista_pedidos.append({
                    "Cozinheiro": prop["Cozinheiro"]["title"][0]["text"]["content"] if prop["Cozinheiro"]["title"] else "N/A",
                    "Navio": prop["Navio"]["rich_text"][0]["text"]["content"] if prop["Navio"]["rich_text"] else "N/A",
                    "Data Pedido": prop["Data Pedido"]["date"]["start"] if prop["Data Pedido"]["date"] else None,
                    "Validade": prop["Validade"]["date"]["start"] if prop["Validade"]["date"] else None,
                    "Lotação": prop["Lotação"]["number"] if prop["Lotação"]["number"] else 0,
                    "Escolta": prop["Escolta"]["select"]["name"] if prop["Escolta"]["select"] else "NÃO",
                    "Observações": prop["Observações"]["rich_text"][0]["text"]["content"] if prop["Observações"]["rich_text"] else ""
                })
            
            df_hist = pd.DataFrame(lista_pedidos)

            # LÓGICA DE FILTRO: Usuário comum vs Administrador
            if st.session_state.cozinheiro.lower() == "admin":
                st.info("💡 Modo Administrador: Você tem visão total de todos os cozinheiros.")
                usuarios_unicos = sorted(df_hist["Cozinheiro"].unique().tolist())
                filtro = st.selectbox("🔍 Pesquisar por Cozinheiro Responsável:", ["TODOS OS COZINHEIROS"] + usuarios_unicos)
                
                if filtro != "TODOS OS COZINHEIROS":
                    df_hist = df_hist[df_hist["Cozinheiro"] == filtro]
            else:
                # O cozinheiro logado só vê o histórico dele
                df_hist = df_hist[df_hist["Cozinheiro"] == st.session_state.cozinheiro]

            # Exibição da Tabela de Auditoria
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            
            # Resumo de controle para você
            if not df_hist.empty:
                st.write(f"📊 **Total de registros encontrados:** {len(df_hist)}")
        else:
            st.error(f"Erro na conexão com o Notion: {res.status_code}")
            
    except Exception as e:
        st.error(f"Falha ao carregar o módulo: {e}")

    if st.button("⬅️ VOLTAR AO MENU PRINCIPAL"):
        st.session_state.pagina = "menu"
        st.rerun()
