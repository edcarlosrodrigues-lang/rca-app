import streamlit as st
import pandas as pd
from datetime import datetime
from github import Github
from io import StringIO
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import io

st.set_page_config(page_title="AQF Industrial - RCA", layout="wide")
st.title("AQF Industrial - Análise de Causa Raiz")
st.warning("USAR SEMPRE PARA PARADAS A PARTIR DE 4 HORAS")

# ========== FUNÇÕES GITHUB ==========
@st.cache_resource
def get_github_repo():
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
    return repo

def salvar_registro(dados):
    try:
        repo = get_github_repo()
        conteudo = repo.get_contents(st.secrets["CSV_PATH"])
        csv_atual = conteudo.decoded_content.decode()
        
        df_novo = pd.DataFrame([dados])
        df_existente = pd.read_csv(StringIO(csv_atual))
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        
        repo.update_file(conteudo.path, "Novo registro AQF", df_final.to_csv(index=False), conteudo.sha)
        return True, "Registro salvo no GitHub!"
    except Exception as e:
        return False, f"Erro ao salvar: {e}"

def carregar_registros():
    try:
        repo = get_github_repo()
        conteudo = repo.get_contents(st.secrets["CSV_PATH"])
        csv = conteudo.decoded_content.decode()
        return pd.read_csv(StringIO(csv))
    except:
        return pd.DataFrame()

# ========== FUNÇÃO PDF ==========
def gerar_pdf(dados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Cabeçalho
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.rect(0, height - 2*cm, width, 2*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 1.3*cm, "AQF Industrial - Análise de Causa Raiz")
    
    # Dados
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y = height - 3*cm
    linha_altura = 0.7*cm
    
    campos = [
        ("Data:", dados["Data"]),
        ("Hora:", dados["Hora"]),
        ("Máquina:", dados["Maquina"]),
        ("Linha:", dados["Linha"]),
        ("Horas de Parada:", f"{dados['Hrs_Parada']}h"),
        ("Responsável:", dados["Resp"]),
        ("", ""),
        ("DESCRIÇÃO DO PROBLEMA:", ""),
        ("", dados["Problema"]),
        ("", ""),
        ("CAUSA RAIZ:", ""),
        ("", dados["Causa_Raiz"]),
        ("", ""),
        ("ISHIKAWA 4M:", ""),
        ("MÉTODO:", dados["Metodo"]),
        ("MÁQUINA:", dados["Maquina_Ish"]),
        ("MÃO DE OBRA:", dados["Mao_Obra"]),
        ("MATERIAL:", dados["Material"]),
    ]
    
    for label, valor in campos:
        if label == "":
            c.setFont("Helvetica", 10)
            for linha in str(valor).split('\n'):
                c.drawString(2.5*cm, y, linha[:90])
                y -= 0.5*cm
        else:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*cm, y, label)
            c.setFont("Helvetica", 11)
            c.drawString(6*cm, y, str(valor)[:60])
            y -= linha_altura
        
        if y < 2*cm:
            c.showPage()
            y = height - 2*cm
    
    c.save()
    buffer.seek(0)
    return buffer

# ========== INTERFACE ==========
tab1, tab2 = st.tabs(["Nova Análise", "Dashboard"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.now())
        hora = st.time_input("Hora", datetime.now().time())
        maquina = st.text_input("Máquina*")
        linha = st.text_input("Linha")
        hrs_parada = st.number_input("Horas de Parada*", min_value=4.0, step=0.5, value=4.0)
        resp = st.text_input("Responsável")
    
    with col2:
        problema = st.text_area("Descrição do Problema*", height=100)
        causa_raiz = st.text_area("Causa Raiz*", height=100)
    
    st.subheader("Ishikawa 4M")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        metodo = st.text_area("**MÉTODO**", height=80)
        maquina_ish = st.text_area("**MÁQUINA**", height=80)
    with col_m2:
        mao_obra = st.text_area("**MÃO DE OBRA**", height=80)
        material = st.text_area("**MATERIAL**", height=80)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Salvar Registro + Gerar PDF", type="primary", use_container_width=True):
            if maquina and problema and causa_raiz:
                dados = {
                    "Data": data.strftime("%d/%m/%Y"),
                    "Hora": hora.strftime("%H:%M"),
                    "Maquina": maquina,
                    "Linha": linha,
                    "Problema": problema,
                    "Causa_Raiz": causa_raiz,
                    "Metodo": metodo,
                    "Maquina_Ish": maquina_ish,
                    "Mao_Obra": mao_obra,
                    "Material": material,
                    "Hrs_Parada": hrs_parada,
                    "Resp": resp
                }
                
                sucesso, msg = salvar_registro(dados)
                if sucesso:
                    st.success(msg)
                    pdf = gerar_pdf(dados)
                    st.download_button(
                        label="📄 Baixar PDF",
                        data=pdf,
                        file_name=f"RCA_{maquina}_{data.strftime('%d%m%Y')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error(msg)
            else:
                st.error("Preencha os campos obrigatórios *")

with tab2:
    st.subheader("Dashboard de Paradas")
    df = carregar_registros()
    
    if df.empty:
        st.info("Nenhum registro ainda. Salve a primeira análise na aba 'Nova Análise'.")
    else:
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        col_d1.metric("Total de Paradas", len(df))
        col_d2.metric("Horas Perdidas", f"{df['Hrs_Parada'].sum():.1f}h")
        col_d3.metric("Média por Parada", f"{df['Hrs_Parada'].mean():.1f}h")
        col_d4.metric("Última Parada", df['Data'].iloc[-1])
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("Pareto: Máquinas")
            df_maq = df['Maquina'].value_counts().reset_index()
            fig1 = px.bar(df_maq, x='Maquina', y='count', 
                         labels={'Maquina':'Máquina', 'count':'Nº Paradas'},
                         color='count', color_continuous_scale='Blues')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_graf2:
            st.subheader("Horas por Máquina")
            df_hrs = df.groupby('Maquina')['Hrs_Parada'].sum().reset_index()
            fig2 = px.bar(df_hrs, x='Maquina', y='Hrs_Parada',
                         labels={'Maquina':'Máquina', 'Hrs_Parada':'Horas'},
                         color='Hrs_Parada', color_continuous_scale='Reds')
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Todos os Registros")
        st.dataframe(df.sort_values('Data', ascending=False), use_container_width=True, height=400)
        
        csv_download = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Baixar todos os registros em CSV",
            data=csv_download,
            file_name=f"registros_aqf_{datetime.now().strftime('%d%m%Y')}.csv",
            mime="text/csv"
        )
