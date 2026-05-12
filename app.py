import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
from github import Github
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===== CONFIGURAÇÃO =====
st.set_page_config(
    page_title="AQF Industrial - RCA",
    page_icon="🏭",
    layout="wide"
)

ARQUIVO_CSV = "registros_aqf.csv"
REPO_NAME = "edcarlosrodrigues-lang/rca-app"  # TROCA PELO SEU REPO

# ===== FUNÇÕES =====
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV)
    else:
        colunas = [
            "Data", "Nº Análise", "Área", "Máquina", "TAG", "Equipamento Parado",
            "Classificação", "Mantenedor", "Turno", "HHD Parada", "Descrição Falha",
            "Máquina_4M", "Método_4M", "Material_4M", "Mão de Obra_4M", "Efeito",
            "Ação Corretiva", "Responsável", "Prazo", "Status"
        ]
        df = pd.DataFrame(columns=colunas)
        df.to_csv(ARQUIVO_CSV, index=False)
        return df

def salvar_github():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(REPO_NAME)
        with open(ARQUIVO_CSV, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        try:
            arquivo = repo.get_contents(ARQUIVO_CSV)
            repo.update_file(ARQUIVO_CSV, f"Update RCA {datetime.now()}", conteudo, arquivo.sha)
        except:
            repo.create_file(ARQUIVO_CSV, f"Create RCA {datetime.now()}", conteudo)
        st.success("Registro salvo no GitHub!")
    except Exception as e:
        st.error(f"Erro ao salvar no GitHub: {e}")
        st.info("Configure o GITHUB_TOKEN nos Secrets do Streamlit Cloud")

def gerar_pdf(dados):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, altura - 50, "AQF INDUSTRIAL - Análise de Causa Raiz")
    
    c.setFont("Helvetica", 12)
    y = altura - 100
    for chave, valor in dados.items():
        if y < 50:
            c.showPage()
            y = altura - 50
        c.drawString(50, y, f"{chave}: {valor}")
        y -= 20
    
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ===== CARREGA DADOS =====
df = carregar_dados()

# ===== HEADER + CARDS =====
st.markdown("# AQF INDUSTRIAL")
st.markdown("### Análise de Causa Raiz - Manufatura & Falhas Industriais")

total_rcas = len(df)
abertos = len(df[df['Status'] == 'Aberto']) if 'Status' in df.columns and not df.empty else 0
em_andamento = len(df[df['Status'] == 'Em Andamento']) if 'Status' in df.columns and not df.empty else 0
concluidos = len(df[df['Status'] == 'Concluído']) if 'Status' in df.columns and not df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TOTAL DE RCAS", total_rcas)
col2.metric("ABERTOS", abertos)
col3.metric("EM ANDAMENTO", em_andamento)
col4.metric("CONCLUÍDOS", concluidos)

st.markdown("---")

# ===== ABAS =====
tab1, tab2, tab3, tab4 = st.tabs(["+ NOVO RCA", "📋 REGISTROS", "📊 DASHBOARD", "📖 GUIA"])

# ===== ABA NOVO RCA =====
with tab1:
    st.subheader("Análise de CAUSA e EFEITO (4M)")
    st.info("💡 Preencha os códigos das causas. Ex: 01-Desgaste")
    
    with st.form("form_rca"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            num_analise = st.text_input("Nº Análise", value=f"MOM-{total_rcas+1:03d}")
            area = st.text_input("Área")
            maquina = st.text_input("Máquina")
            tag = st.text_input("TAG")
            equip_parado = st.selectbox("Equipamento Parado", ["SIM", "NÃO"])
            classificacao = st.selectbox("Classificação", ["FALHA", "QUEBRA", "PARADA"])
            
        with col_b:
            mantenedor = st.text_input("Mantenedor")
            turno = st.selectbox("Turno", ["1º Turno", "2º Turno", "3º Turno"])
            hhd_parada = st.number_input("HHD Parada", min_value=0.0, step=0.5)
            descricao = st.text_area("Descrição da Falha")
        
        st.markdown("#### PADRÃO")
        st.text_input("Padrão", label_visibility="collapsed")
        
        st.markdown("#### Análise de CAUSA e EFEITO (4M)")
        col_4m1, col_4m2 = st.columns(2)
        
        with col_4m1:
            st.markdown("**Máquina**")
            maquina_4m = st.text_area("Máquina 4M", placeholder="01-Desgaste\n02-Folga", height=100, label_visibility="collapsed")
            st.markdown("**Método**")
            metodo_4m = st.text_area("Método 4M", placeholder="09-Falta preventiva", height=100, label_visibility="collapsed")
        
        with col_4m2:
            st.markdown("**Material**")
            material_4m = st.text_area("Material 4M", placeholder="05-Vedação ressecada", height=100, label_visibility="collapsed")
            st.markdown("**Mão de Obra**")
            mao_obra_4m = st.text_area("Mão de Obra 4M", placeholder="13-Falta treinamento", height=100, label_visibility="collapsed")
        
        efeito = st.text_input("Efeito da Falha/Defeito")
        
        st.markdown("---")
        acao = st.text_input("Ação Corretiva")
        responsavel = st.text_input("Responsável")
        prazo = st.date_input("Prazo")
        status = st.selectbox("Status", ["Aberto", "Em Andamento", "Concluído"])
        
        col_btn1, col_btn2 = st.columns(2)
        salvar = col_btn1.form_submit_button("💾 Salvar RCA", use_container_width=True)
        gerar_pdf_btn = col_btn2.form_submit_button("📄 Gerar PDF da Análise", use_container_width=True)
        
        if salvar or gerar_pdf_btn:
            novo_registro = {
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Nº Análise": num_analise,
                "Área": area,
                "Máquina": maquina,
                "TAG": tag,
                "Equipamento Parado": equip_parado,
                "Classificação": classificacao,
                "Mantenedor": mantenedor,
                "Turno": turno,
                "HHD Parada": hhd_parada,
                "Descrição Falha": descricao,
                "Máquina_4M": maquina_4m,
                "Método_4M": metodo_4m,
                "Material_4M": material_4m,
                "Mão de Obra_4M": mao_obra_4m,
                "Efeito": efeito,
                "Ação Corretiva": acao,
                "Responsável": responsavel,
                "Prazo": prazo.strftime("%d/%m/%Y"),
                "Status": status
            }
            
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
            df.to_csv(ARQUIVO_CSV, index=False)
            salvar_github()
            
            if gerar_pdf_btn:
                pdf = gerar_pdf(novo_registro)
                st.download_button(
                    label="⬇️ Baixar PDF",
                    data=pdf,
                    file_name=f"RCA_{num_analise}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            
            st.rerun()

# ===== ABA REGISTROS =====
with tab2:
    st.subheader("📋 REGISTROS DE ANÁLISES MOM")
    st.write(f"Total de registros: {len(df)}")
    
    if not df.empty:
        col_f1, col_f2, col_f3 = st.columns([2,2,1])
        filtro_area = col_f1.selectbox("Filtrar por Área", ["Todas"] + df['Área'].unique().tolist())
        filtro_status = col_f2.selectbox("Filtrar por Status", ["Todos"] + df['Status'].unique().tolist())
        
        df_filtrado = df.copy()
        if filtro_area != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Área'] == filtro_area]
        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Status'] == filtro_status]
            
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
        if col_f3.button("🗑️ Limpar Tudo"):
            df = df.iloc[0:0]
            df.to_csv(ARQUIVO_CSV, index=False)
            salvar_github()
            st.rerun()
    else:
        st.info("Nenhum registro cadastrado ainda.")

# ===== ABA DASHBOARD =====
with tab3:
    st.subheader("📊 DASHBOARD")
    if not df.empty:
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown("**RCAs por Área**")
            st.bar_chart(df['Área'].value_counts())
        
        with col_d2:
            st.markdown("**RCAs por Status**")
            st.bar_chart(df['Status'].value_counts())
            
        st.markdown("**RCAs por Classificação**")
        st.bar_chart(df['Classificação'].value_counts())
    else:
        st.info("Cadastre o primeiro RCA para ver os gráficos.")

# ===== ABA GUIA =====
with tab4:
    st.subheader("📖 GUIA DE PREENCHIMENTO")
    st.markdown("""
    **Códigos 4M - Máquina:**
    - 01-Desgaste
    - 02-Folga
    - 03-Quebra
    - 04-Vibração
    
    **Códigos 4M - Método:**
    - 09-Falta preventiva
    - 10-Procedimento incorreto
    - 11-Falta de padrão
    
    **Códigos 4M - Material:**
    - 05-Vedação ressecada
    - 06-Material inadequado
    - 07-Contaminação
    
    **Códigos 4M - Mão de Obra:**
    - 13-Falta treinamento
    - 14-Falha operacional
    - 15-Desatenção
    """)