import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from io import BytesIO

st.set_page_config(
    page_title="AQF Industrial - RCA",
    layout="wide",
    page_icon="🏭"
)

# CSS AQF INDUSTRIAL
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #C00000;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #1B3448;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #C00000;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        height: 3em;
        border: none;
    }
    .stButton > button:hover {
        background-color: #8B0000;
        color: white;
    }
    .stDownloadButton > button {
        background-color: #1B3448;
        color: white;
        font-weight: bold;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def gerar_pdf_aqf(dados_mom):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # CORES AQF
    vermelho_aqf = colors.HexColor('#C00000')
    azul_escuro = colors.HexColor('#1B3448')
    cinza_claro = colors.HexColor('#F2F2F2')
    cor_borda = colors.HexColor('#808080')

    # ESTILOS AQF
    style_titulo = ParagraphStyle(
        'TituloAQF',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=vermelho_aqf,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    style_empresa = ParagraphStyle(
        'Empresa',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=azul_escuro,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    style_subtitulo = ParagraphStyle(
        'SubtituloAQF',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.white,
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        backColor=vermelho_aqf,
        leftIndent=6,
        rightIndent=6
    )

    style_normal = ParagraphStyle(
        'NormalAQF',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )

    style_label = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=azul_escuro,
        fontName='Helvetica-Bold'
    )

    # CABEÇALHO AQF INDUSTRIAL
    elements.append(Paragraph("AQF INDUSTRIAL", style_empresa))
    elements.append(Paragraph("RELATÓRIO DE ANÁLISE DE FALHA - RCA", style_titulo))
    elements.append(Spacer(1, 0.4*cm))

    # DATA/HORA
    data_ocorrencia = dados_mom.get('data_ocorrencia')
    hora_ocorrencia = dados_mom.get('hora_ocorrencia')
    data_formatada = data_ocorrencia.strftime('%d/%m/%Y') if data_ocorrencia else '-'
    hora_formatada = hora_ocorrencia.strftime('%H:%M') if hora_ocorrencia else '-'

    # TABELA CABEÇALHO DADOS
    dados_cabecalho = [
        [Paragraph('<b>Nº MOM:</b>', style_label), dados_mom.get('num_mom', '-'), 
         Paragraph('<b>DATA:</b>', style_label), data_formatada],
        [Paragraph('<b>ÁREA:</b>', style_label), dados_mom.get('area', '-'), 
         Paragraph('<b>HORA:</b>', style_label), hora_formatada],
        [Paragraph('<b>EQUIPAMENTO:</b>', style_label), dados_mom.get('equipamento', '-'), 
         Paragraph('<b>TURNO:</b>', style_label), dados_mom.get('turno', '-')],
        [Paragraph('<b>RESPONSÁVEL:</b>', style_label), dados_mom.get('responsavel', '-'), 
         Paragraph('<b>SETOR:</b>', style_label), dados_mom.get('setor', '-')],
    ]

    tabela_cab = Table(dados_cabecalho, colWidths=[3*cm, 6*cm, 2.5*cm, 6*cm])
    tabela_cab.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1.5, vermelho_aqf),
        ('BACKGROUND', (0, 0), (0, -1), cinza_claro),
        ('BACKGROUND', (2, 0), (2, -1), cinza_claro),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(tabela_cab)
    elements.append(Spacer(1, 0.6*cm))

    # SEÇÕES AQF
    secoes = [
        ('1. DESCRIÇÃO DA OCORRÊNCIA', dados_mom.get('descricao', 'Não informado')),
        ('2. ANÁLISE DA CAUSA RAIZ', dados_mom.get('analise_causa', 'Não informado')),
        ('3. AÇÕES CORRETIVAS IMEDIATAS', dados_mom.get('acoes_corretivas', 'Não informado')),
        ('4. AÇÕES PREVENTIVAS', dados_mom.get('acoes_preventivas', 'Não informado')),
    ]

    for titulo, conteudo in secoes:
        elements.append(Paragraph(titulo, style_subtitulo))
        elements.append(Spacer(1, 0.2*cm))
        
        # Caixa de conteúdo
        conteudo_table = Table([[Paragraph(conteudo, style_normal)]], colWidths=[17.5*cm])
        conteudo_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, cor_borda),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(conteudo_table)
        elements.append(Spacer(1, 0.4*cm))

    # CAMPO DE ASSINATURA AQF
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph('5. APROVAÇÕES', style_subtitulo))
    elements.append(Spacer(1, 0.5*cm))

    assinatura_data = [
        ['_________________________', '_________________________'],
        ['Técnico Responsável', 'Supervisor de Manutenção', 'Gerente Industrial'],
        ['Nome: ________________', 'Nome: ________________', 'Nome: ________________'],
        ['Data: ___/___/______', 'Data: ___/___/______', 'Data: ___/___/______'],
    ]

    tabela_ass = Table(assinatura_data, colWidths=[5.8*cm, 5.8*cm, 5.8*cm])
    tabela_ass.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEABOVE', (0,1), (-1,1), 1, cor_borda),
    ]))

    elements.append(tabela_ass)

    # RODAPÉ
    elements.append(Spacer(1, 0.8*cm))
    data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    rodape_style = ParagraphStyle('Rodape', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"AQF Industrial - Documento gerado em {data_geracao}", rodape_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# INTERFACE AQF
st.markdown('<p class="main-header">🏭 AQF INDUSTRIAL</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Sistema de Análise de Falhas - RCA/MOM</p>', unsafe_allow_html=True)

with st.expander("📋 Instruções de Preenchimento", expanded=False):
    st.markdown("""
    **Campos obrigatórios marcados com ***  
    1. Preencha todos os dados da ocorrência
    2. Descreva com detalhes usando método 5 Porquês
    3. Defina ações corretivas e preventivas
    4. Gere o PDF para impressão e assinaturas
    """)

st.markdown("### 📌 Dados da Ocorrência")

col1, col2 = st.columns(2)

with col1:
    num_mom = st.text_input("Nº MOM *", placeholder="AQF-2026-001")
    area = st.text_input("Área *", placeholder="Ex: Laminação")
    equipamento = st.text_input("Equipamento *", placeholder="Ex: Ponte Rolante 05")
    responsavel = st.text_input("Responsável Técnico *", placeholder="Ex: João Silva")

with col2:
    data_ocorrencia = st.date_input("Data da Ocorrência *", value=date.today())
    hora_ocorrencia = st.time_input("Hora da Ocorrência *", value=datetime.now().time())
    turno = st.selectbox("Turno *", ["Manhã", "Tarde", "Noite", "Administrativo"])
    setor = st.text_input("Setor *", placeholder="Ex: Manutenção Mecânica")

st.markdown("### 📝 Análise Detalhada")

descricao = st.text_area("1. Descrição da Ocorrência *", height=120, 
                         placeholder="Descreva detalhadamente o que aconteceu, quando, onde e como...")
analise_causa = st.text_area("2. Análise da Causa Raiz *", height=120, 
                             placeholder="Use método 5 Porquês, Ishikawa, etc...")
acoes_corretivas = st.text_area("3. Ações Corretivas Imediatas *", height=100, 
                                placeholder="O que foi feito para corrigir imediatamente...")
acoes_preventivas = st.text_area("4. Ações Preventivas *", height=100, 
                                 placeholder="O que será feito para evitar recorrência...")

st.markdown("---")

col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
with col_btn2:
    if st.button("🔄 GERAR RELATÓRIO PDF", type="primary", use_container_width=True):
        if not all([num_mom, area, equipamento, responsavel, descricao]):
            st.error("⚠️ Preencha todos os campos obrigatórios (*)")
        else:
            dados = {
                'num_mom': num_mom, 'area': area, 'equipamento': equipamento,
                'responsavel': responsavel, 'data_ocorrencia': data_ocorrencia,
                'hora_ocorrencia': hora_ocorrencia, 'turno': turno, 'setor': setor,
                'descricao': descricao, 'analise_causa': analise_causa,
                'acoes_corretivas': acoes_corretivas, 'acoes_preventivas': acoes_preventivas,
            }

            with st.spinner("Gerando documento AQF..."):
                pdf_buffer = gerar_pdf_aqf(dados)

            st.success("✅ Relatório AQF gerado com sucesso!")

            st.download_button(
                label="📥 BAIXAR PDF",
                data=pdf_buffer,
                file_name=f"AQF_RCA_{num_mom}_{data_ocorrencia.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )