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
# --- BLOCO 8: TELA DE HISTÓRICO ---
elif st.session_state.pagina == "historico":
    aplicar_estilo_azul(); st.title("📜 Histórico de Registros")
    try:
        url_h = f"https://api.notion.com/v1/databases/{ID_HISTORICO_NOTION}/query"
        headers_h = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
        payload = {"filter": {"property": "Navio", "rich_text": {"equals": st.session_state.navio}}}
        res = requests.post(url_h, headers=headers_h, json=payload)
        if res.status_code == 200:
            results = res.json().get("results", [])
            dados_h = [{"Data": r["properties"]["Data Pedido"]["date"]["start"], "Responsável": r["properties"]["Cozinheiro"]["title"][0]["text"]["content"], "Validade": r["properties"]["Validade"]["date"]["start"]} for r in results if r["properties"]["Cozinheiro"]["title"]]
            st.dataframe(pd.DataFrame(dados_h), use_container_width=True, hide_index=True)
        else: st.warning("Sem registros.")
    except: st.error("Erro ao carregar módulo.")
    if st.button("⬅️ VOLTAR AO MENU"): st.session_state.pagina = "menu"; st.rerun()

# =================================================================
# BLOCO 7: TELA DE DECLARAÇÃO (FORMATO DE DATA BRASILEIRO)
# =================================================================
elif st.session_state.pagina == "tripulacao":
    aplicar_estilo_tecnologico()
    
    # Cabeçalho da Tela
    st.markdown("<h2>⚓ Declaração de Reabastecimento</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Grid de Informações
    col1, col2 = st.columns(2)
    with col1:
        responsavel = st.text_input("Responsável pelo Registro", value=st.session_state.cozinheiro, disabled=True)
        # CORREÇÃO: Formato de data ajustado para DD/MM/YYYY
        data_ultimo = st.date_input("Data do Último Rancho", format="DD/MM/YYYY")
        origem = st.text_input("Origem", value="Porto Velho")
    
    with col2:
        # CORREÇÃO: Formato de data ajustado para DD/MM/YYYY
        data_pedido = st.date_input("Data do Pedido", value=datetime.now(), format="DD/MM/YYYY")
        escolta = st.selectbox("A embarcação possui Escolta?", ["NÃO", "SIM"])
        destino = st.text_input("Destino", value="Novo remanso")

    qtd_tripulantes = st.number_input("Quantidade de Tripulantes a bordo", min_value=1, value=14, step=1)

    # Lógica de Dias
    dias = 12 if escolta == "SIM" else 15
    vencimento = data_pedido + timedelta(days=dias)
    
    # Quadro de Aviso com data em português
    st.markdown(f"""
        <div class="mensagem-validade">
            📢 Devido à presença de escolta: {escolta}<br>
            A duração estimada do rancho é de {dias} dias.<br>
            Validade prevista até: {vencimento.strftime('%d/%m/%Y')}
        </div>
    """, unsafe_allow_html=True)

    # Assinatura - Título conforme imagem 1
    st.markdown("### ✍️ Assinatura do Comandante/Encarregado")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.3)", stroke_width=2,
        stroke_color="#000000", background_color="#FFFFFF",
        height=150, update_streamlit=True, key="canvas_bloco7_final_v2"
    )

    # Campo de Observação (Considerações)
    consideracoes = st.text_area("CONSIDERAÇÕES:", placeholder="Digite aqui observações importantes...")

    # Botões de Ação
    st.markdown("---")
    b_gerar, b_voltar = st.columns(2)
    
    with b_gerar:
        if st.button("📄 GERAR PDF DA DECLARAÇÃO"):
            if canvas_result.image_data is not None:
                fuso_br = pytz.timezone('America/Sao_Paulo')
                agora_br = datetime.now(fuso_br)
                data_hora_br = agora_br.strftime('%d/%m/%Y %H:%M:%S')

                pdf = FPDF(); pdf.add_page()
                if os.path.exists("ZION.jpg"): pdf.image("ZION.jpg", 90, 10, 25)
                
                pdf.set_font("Arial", "B", 14); pdf.set_y(40)
                pdf.cell(0, 10, preparar("DECLARAÇÃO DE REABASTECIMENTO"), ln=True, align="C")
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, preparar(f"Embarcação: {st.session_state.navio}"), ln=True, align="C")
                
                # Texto da Carta com Datas Formatadas DD/MM/YYYY
                pdf.set_font("Arial", "", 11); pdf.ln(10)
                texto_corpo = (
                    f"Pelo presente, certifico que a lotação de tripulantes a bordo do empurrador é de {qtd_tripulantes} tripulantes. "
                    f"A provisão de rancho a ser reabastecida destina-se a cobrir as necessidades nutricionais da "
                    f"tripulação por um período de {dias} dias náuticos a partir de {data_pedido.strftime('%d/%m/%Y')}. "
                    f"Este suprimento é planejado para a viagem corrente."
                )
                pdf.multi_cell(0, 8, preparar(texto_corpo))
                
                pdf.ln(5); pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, preparar(f"Origem: {origem} | Destino: {destino}"), ln=True)
                # Data no PDF corrigida
                pdf.cell(0, 8, preparar(f"Último Rancho: {data_ultimo.strftime('%d/%m/%Y')}"), ln=True)
                
                if consideracoes:
                    pdf.ln(5); pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 8, "CONSIDERAÇÕES:", ln=True)
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(0, 7, preparar(consideracoes))

                # Assinatura e Rodapé
                img_path = "assinatura_temp.png"
                Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').save(img_path)
                pdf.image(img_path, x=75, y=pdf.get_y() + 5, w=50)
                
                pdf.set_y(pdf.get_y() + 25)
                pdf.line(60, pdf.get_y(), 150, pdf.get_y())
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 8, preparar(f"Responsável: {st.session_state.cozinheiro}"), ln=True, align="C")
                
                pdf.set_font("Arial", "I", 7)
                pdf.cell(0, 5, preparar(f"Registro oficial gerado em: {data_hora_br} (Brasília)"), ln=True, align="C")
                
                st.download_button("📥 BAIXAR DECLARAÇÃO", pdf.output(dest='S').encode('latin-1'), 
                                 f"Declaracao_{st.session_state.navio}.pdf", "application/pdf")
                st.success("✅ PDF Gerado com sucesso!")
            else:
                st.warning("Assine no campo branco antes de gerar o arquivo.")

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
