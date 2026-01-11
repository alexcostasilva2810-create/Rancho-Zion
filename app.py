import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
import unicodedata
from fpdf import FPDF
from PIL import Image
import os
import requests
import pytz

# =================================================================
# BLOCO 1: CONFIGURAÇÕES, IDs E ESTILOS GERAIS
# =================================================================
st.set_page_config(page_title="Zion Rancho App", layout="wide")

# Credenciais e IDs
NOTION_TOKEN = "ntn_jZ6353375938j9kJFqKWjD0N4ONt1rwP515tsIMwxtucHa"
DATABASE_ID = "2e3025de7b79803abe0efde74f87a2e1" 
ID_HISTORICO_NOTION = "2e5025de7b79803187a4d8b865179440"

# Inicialização de Variáveis de Estado
if 'pagina' not in st.session_state: st.session_state.pagina = "home"
if 'cozinheiro' not in st.session_state: st.session_state.cozinheiro = ""
if 'navio' not in st.session_state: st.session_state.navio = ""
if 'df_lista' not in st.session_state: st.session_state.df_lista = pd.DataFrame(columns=["ITEM", "DESCRIÇÃO", "TIPO", "UNID MED", "PREDEFINIDO", "CONFIRMA"])

# Funções Utilitárias
def preparar(t): return unicodedata.normalize('NFKD', str(t)).encode('latin-1', 'ignore').decode('latin-1')

def aplicar_estilo_tecnologico():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 20, 50, 0.88), rgba(0, 20, 50, 0.88)), 
            url('https://images.unsplash.com/photo-1544383333-546e16fd3a51?q=80&w=1920');
            background-size: cover; background-position: center;
        }
        h1, h2, h3, p, label { color: white !important; }
        .stButton > button {
            border: 1px solid #00D4FF !important; background: rgba(0, 212, 255, 0.1) !important;
            color: white !important; border-radius: 8px; width: 100%; height: 50px; font-weight: bold;
        }
        .stButton > button:hover { background: #00D4FF !important; color: black !important; }
        .mensagem-validade { 
            background-color: rgba(60, 45, 30, 0.9); 
            padding: 20px; border-radius: 8px; border-left: 6px solid #FF8C00;
            color: white; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# =================================================================
# BLOCO 2: TELA HOME (ZION TECNOLOGIA)
# =================================================================
if st.session_state.pagina == "home":
    st.markdown("<style>.stApp { background-color: #4169E1; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Zion Tecnologia</h1>", unsafe_allow_html=True)
    if os.path.exists("ZION.jpg"): st.image("ZION.jpg", use_container_width=True)
    if st.button("🚀 ACESSAR SISTEMA"): st.session_state.pagina = "login"; st.rerun()

# =================================================================
# BLOCO 3: TELA DE LOGIN
# =================================================================
elif st.session_state.pagina == "login":
    st.title("🔐 Login")
    navio_sel = st.selectbox("Selecione a Embarcação", ["NAVIO 01", "AROEIRA", "NAVIO 03"])
    nome_user = st.text_input("Nome do Cozinheiro Responsável")
    if st.button("ENTRAR NO SISTEMA"):
        if nome_user:
            st.session_state.cozinheiro = nome_user
            st.session_state.navio = navio_sel
            st.session_state.pagina = "menu"; st.rerun()
        else: st.warning("Por favor, informe seu nome.")

# =================================================================
# BLOCO 4: MENU PRINCIPAL (PROFISSIONAL)
# =================================================================
elif st.session_state.pagina == "menu":
    aplicar_estilo_tecnologico()
    h1, h2 = st.columns([1, 6])
    with h1: 
        if os.path.exists("ZION.jpg"): st.image("ZION.jpg", width=80)
    with h2: st.markdown(f"<h1>Painel - {st.session_state.navio}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📋 TABELA DE RANCHO", use_container_width=True): st.session_state.pagina = "lista"; st.rerun()
        if st.button("📜 VER HISTÓRICO", use_container_width=True): st.session_state.pagina = "historico"; st.rerun()
    with c2:
        if st.button("👨‍✈️ DECLARAÇÃO", use_container_width=True): st.session_state.pagina = "tripulacao"; st.rerun()
        if st.button("⬅️ SAIR", use_container_width=True): st.session_state.pagina = "home"; st.rerun()

# =================================================================
# BLOCO 6: CONFERÊNCIA DE ESTOQUE (MAPEAMENTO DINÂMICO E ROBUSTO)
# =================================================================
elif st.session_state.pagina == "lista":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho com Logo Lateral restaurada
    col_logo, col_tit = st.columns([1, 8])
    with col_logo:
        if os.path.exists("ZION.jpg"): 
            st.image("ZION.jpg", width=80)
    with col_tit:
        st.markdown("<h1 style='color: white; margin-top: 10px;'>📋 Conferência de Estoque</h1>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Botão de Atualização com Mapeamento Flexível
    if st.button("🔄 ATUALIZAR DADOS DO NOTION", use_container_width=True):
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        try:
            response = requests.post(f"https://api.notion.com/v1/databases/{DATABASE_ID}/query", headers=headers)
            if response.status_code == 200:
                data = response.json()
                itens = []
                for page in data["results"]:
                    p = page["properties"]
                    
                    # --- LÓGICA DE CAPTURA FLEXÍVEL ---
                    
                    # 1. Busca o CÓDIGO (ITEM) - Tenta várias grafias
                    id_item = 0
                    for key in ["ITEM", "Item", "item", "COD", "CÓDIGO"]:
                        if key in p and p[key].get("number") is not None:
                            id_item = p[key]["number"]
                            break
                    
                    # 2. Busca a DESCRIÇÃO (Coluna Principal do Notion)
                    desc = "Sem Descrição"
                    for key in ["DESCRIÇÃO", "Descricao", "Nome", "Name"]:
                        if key in p and p[key].get("title"):
                            if len(p[key]["title"]) > 0:
                                desc = p[key]["title"][0]["text"]["content"]
                                break
                    
                    # 3. Busca a UNIDADE DE MEDIDA
                    unid = "un"
                    for key in ["UNID MED", "UNIDADE", "Unid", "Medida"]:
                        if key in p and p[key].get("select"):
                            unid = p[key]["select"]["name"]
                            break
                    
                    itens.append({
                        "ITEM": id_item,
                        "DESCRIÇÃO": desc,
                        "UNID MED": unid,
                        "CONFIRMA": 0
                    })
                
                # Atualiza e ordena
                if itens:
                    st.session_state.df_lista = pd.DataFrame(itens).sort_values(by="ITEM")
                    st.success(f"✅ Sucesso! {len(itens)} itens carregados do Notion.")
                else:
                    st.warning("⚠️ O Notion respondeu, mas a lista veio vazia. Verifique os filtros no Notion.")
                st.rerun()
            else:
                st.error(f"Erro de Conexão: Status {response.status_code}")
        except Exception as e:
            st.error(f"Erro Crítico: {str(e)}")

    # Exibição da Tabela Corrigida
    df_editado = st.data_editor(
        st.session_state.df_lista,
        column_config={
            "ITEM": st.column_config.NumberColumn("CÓD.", disabled=True),
            "DESCRIÇÃO": st.column_config.TextColumn("DESCRIÇÃO", disabled=True),
            "UNID MED": st.column_config.TextColumn("UNID", disabled=True),
            "CONFIRMA": st.column_config.NumberColumn("CONFIRMA", min_value=0)
        },
        hide_index=True,
        use_container_width=True,
        key="editor_estoque_v_notion_final"
    )

    st.markdown("---")
    # Ações
    c_pdf, c_voltar = st.columns(2)
    with c_pdf:
        if st.button("💾 GERAR E SALVAR RELATÓRIO"):
            fuso_br = pytz.timezone('America/Sao_Paulo')
            data_hora = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M:%S')
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 95, 8, 20)
            pdf.set_font("Arial", "B", 14); pdf.set_y(35)
            pdf.cell(0, 10, preparar(f"Relatório de Rancho: {st.session_state.navio}"), ln=True, align="C")
            pdf.ln(10)
            pdf.set_fill_color(200, 220, 255); pdf.set_font("Arial", "B", 8)
            pdf.cell(20, 8, "COD", 1, 0, "C", True)
            pdf.cell(110, 8, "DESCRICAO", 1, 0, "L", True)
            pdf.cell(30, 8, "CONFIRMA", 1, 1, "C", True)
            pdf.set_font("Arial", "", 8)
            for _, row in df_editado.iterrows():
                pdf.cell(20, 7, str(row["ITEM"]), 1, 0, "C")
                pdf.cell(110, 7, preparar(str(row["DESCRIÇÃO"])), 1, 0, "L")
                pdf.cell(30, 7, str(row["CONFIRMA"]), 1, 1, "C")
            st.download_button("📥 BAIXAR PDF", data=pdf.output(dest='S').encode('latin-1'), file_name="Rancho.pdf")

    with c_voltar:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: TELA DE DECLARAÇÃO (CENTRALIZADA E AJUSTADA)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho Centralizado
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/seu-repositorio/ZION.jpg" width="70">
            <h2 style="color: white; margin-top: 10px;">⚓ Declaração de Reabastecimento</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Campos de Entrada
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Responsável pelo Registro", value=st.session_state.cozinheiro, disabled=True)
        data_ultimo = st.date_input("Data do Último Rancho", format="DD/MM/YYYY")
        origem = st.text_input("Origem", value="Porto Velho")
    with col2:
        data_pedido = st.date_input("Data do Pedido", value=datetime.now(), format="DD/MM/YYYY")
        escolta = st.selectbox("A embarcação possui Escolta?", ["NÃO", "SIM"])
        destino = st.text_input("Destino", value="Novo remanso")

    qtd_tripulantes = st.number_input("Quantidade de Tripulantes a bordo", min_value=1, value=14)

    # Cálculo e Mensagem de Validade
    dias = 12 if escolta == "SIM" else 15
    vencimento = data_pedido + timedelta(days=dias)
    
    st.markdown(f"""
        <div class="mensagem-validade">
            📢 Escolta: {escolta} | Duração: {dias} dias<br>
            Validade prevista até: {vencimento.strftime('%d/%m/%Y')}
        </div>
    """, unsafe_allow_html=True)

    # Assinatura
    st.markdown("### ✍️ Assinatura do Comandante/Encarregado")
    canvas_result = st_canvas(fill_color="white", stroke_width=2, stroke_color="black", background_color="white", height=150, key="canvas_declaracao")
    
    consideracoes = st.text_area("CONSIDERAÇÕES:", placeholder="Descreva aqui observações importantes...")

    st.markdown("---")
    b_gerar, b_voltar = st.columns(2)
    
    with b_gerar:
        if st.button("📄 GERAR PDF DA DECLARAÇÃO"):
            if canvas_result.image_data is not None:
                fuso_br = pytz.timezone('America/Sao_Paulo')
                data_hora_br = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M:%S')

                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 25)
                
                pdf.set_font("Arial", "B", 14); pdf.set_y(45)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, preparar(f"Embarcação: {st.session_state.navio}"), ln=True, align="C")
                
                pdf.set_font("Arial", "", 11); pdf.ln(10)
                corpo = (f"Pelo presente, certifico que a lotação de tripulantes a bordo do empurrador é de {qtd_tripulantes} tripulantes. "
                         f"A provisão de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da "
                         f"tripulação por um período de {dias} dias náuticos a partir de {data_pedido.strftime('%d/%m/%Y')}.")
                pdf.multi_cell(0, 8, preparar(corpo))
                
                pdf.ln(5); pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, preparar(f"Origem: {origem} | Destino: {destino}"), ln=True)
                pdf.cell(0, 8, preparar(f"Último Rancho: {data_ultimo.strftime('%d/%m/%Y')}"), ln=True)

                if consideracoes:
                    pdf.ln(5); pdf.cell(0, 8, "CONSIDERAÇÕES:", ln=True)
                    pdf.set_font("Arial", "", 11); pdf.multi_cell(0, 7, preparar(consideracoes))

                # Assinatura no PDF
                img_path = "temp_assinatura.png"
                Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').save(img_path)
                pdf.image(img_path, x=75, y=pdf.get_y() + 5, w=50)
                
                pdf.set_y(pdf.get_y() + 25); pdf.line(60, pdf.get_y(), 150, pdf.get_y())
                pdf.set_font("Arial", "", 10); pdf.cell(0, 8, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True, align="C")
                pdf.set_font("Arial", "I", 7); pdf.cell(0, 5, preparar(f"Gerado em: {data_hora_br} (Brasília)"), ln=True, align="C")
                
                st.download_button("📥 BAIXAR DECLARAÇÃO PDF", pdf.output(dest='S').encode('latin-1'), f"Declaracao_{st.session_state.navio}.pdf", "application/pdf")
                st.success("✅ PDF da Declaração gerado!")
    
    with b_voltar:
        if st.button("⬅️ VOLTAR AO MENU"):
            st.session_state.pagina = "menu"; st.rerun()
# =================================================================
# BLOCO 8: TELA DE HISTÓRICO
# =================================================================
elif st.session_state.pagina == "historico":
    aplicar_estilo_tecnologico()
    st.title("📜 Histórico de Registros")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()
