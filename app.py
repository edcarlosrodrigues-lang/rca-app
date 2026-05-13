import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from io import BytesIO

st.set_page_config(
    page_title="RCA - Análise de Falhas",
    layout="wide",
    page_icon="📋"
)

# CSS PRA DEIXAR BONITO
st.markdown("""
<style>
   .main > div {
        padding-top: 2rem;
    }
   .stButton > button {
        background-color: #1B3448;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        height: 3em;
    }
   .stDownloadButton > button {
        background-color: #28a745;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def gerar_pdf_mom(dados_mom):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # CORES
    cor_primaria = colors.HexColor('#1B3448')
    cor_secundaria = colors.HexColor('#F5F5F5')
    cor_borda = colors.HexColor('#CCCCCC')

    # ESTILOS
    style_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=cor_primaria,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=cor_primaria,
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )

    # CABEÇALHO COM BORDA
    elements.append(Paragraph("RELATÓRIO DE ANÁLISE DE FALHA - RCA", style_titulo))
    elements.append(Paragraph("Minutes of Meeting - MOM", style_subtitulo))
    elements.append(Spacer(1, 0.3*cm))

    # LINHA DIVISÓRIA
    linha = Table([['']], colWidths=[17*cm])
    linha.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 2, cor_primaria)]))
    elements.append(linha)
    elements.append(Spacer(1, 0.5*cm))

    # TRATAMENTO DATA/HORA
    data_ocorrencia = dados_mom.get('data_ocorrencia')
    hora_ocorrencia = dados_mom.get('hora_ocorrencia')
    data_formatada = data_ocorrencia.strftime('%d/%m/%Y') if data_ocorrencia else 'Não informado'
    hora_formatada = hora_ocorrencia.strftime('%H:%M') if hora_ocorrencia else 'Não informado'

    # TABELA PRINCIPAL
    dados_tabela = [
        ['Nº MOM', dados_mom.get('num_mom', '-'), 'DATA DA OCORRÊNCIA', data_formatada],
        ['ÁREA', dados_mom.get('area', '-'), 'TURNO', dados_mom.get('turno', '-')],
        ['EQUIPAMENTO', dados_mom.get('equipamento', '-'), 'HORA', hora_formatada],
        ['RESPONSÁVEL', dados_mom.get('responsavel', '-'), 'SETOR', dados_mom.get('setor', '-')],
    ]

    tabela = Table(dados_tabela, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), cor_secundaria),
        ('BACKGROUND', (2, 0), (2, -1), cor_secundaria),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, cor_borda),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(tabela)
    elements.append(Spacer(1, 0.8*cm))

    # SEÇÕES COM CAIXA
    secoes = [
        ('DESCRIÇÃO DA OCORRÊNCIA', dados_mom.get('descricao', 'Não informado')),
        ('ANÁLISE DA CAUSA RAIZ', dados_mom.get('analise_causa', 'Não informado')),
        ('AÇÕES CORRETIVAS', dados_mom.get('acoes_corretivas', 'Não informado')),
        ('AÇÕES PREVENTIVAS', dados_mom.get('acoes_preventivas', 'Não informado')),
    ]

    for titulo, conteudo in secoes:
        # Título da seção com fundo
        titulo_box = Table([[titulo]], colWidths=[17*cm])
        titulo_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), cor_primaria),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(titulo_box)
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(conteudo, style_normal))
        elements.append(Spacer(1, 0.5*cm))

    # CAMPO DE ASSINATURA
    elements.append(Spacer(1, 1.5*cm))
    elements.append(Paragraph("APROVAÇÕES", style_subtitulo))
    elements.append(Spacer(1, 0.5*cm))

    assinatura_data = [
        ['_______________________________', '_______________________________'],
        ['Responsável Técnico', 'Supervisor da Área', 'Gerente de Manutenção'],
        ['Data: ___/___/______', 'Data: ___/___/______', 'Data: ___/___/______'],
    ]

    tabela_ass = Table(assinatura_data, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
    tabela_ass.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))

    elements.append(tabela_ass)

    # RODAPÉ
    elements.append(Spacer(1, 1*cm))
    data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    rodape_style = ParagraphStyle('Rodape', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Documento gerado em {data_geracao} - Sistema RCA", rodape_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# INTERFACE
st.title("📋 Gerador de RCA - Minutes of Meeting")
st.caption("Sistema profissional para análise de falhas de manutenção")

with st.expander("ℹ️ Como usar", expanded=False):
    st.info("Preencha todos os campos abaixo e clique em 'Gerar PDF'. O documento será formatado automaticamente com campo de assinatura.")

col1, col2 = st.columns(2)

with col1:
    num_mom = st.text_input("Nº MOM *", placeholder="Ex: 2026-001")
    area = st.text_input("Área *", placeholder="Ex: Laminação")
    equipamento = st.text_input("Equipamento *", placeholder="Ex: Ponte Rolante 05")
    responsavel = st.text_input("Responsável *", placeholder="Ex: João Silva")

with col2:
    data_ocorrencia = st.date_input("Data da Ocorrência *", value=date.today())
    hora_ocorrencia = st.time_input("Hora da Ocorrência *", value=datetime.now().time())
    turno = st.selectbox("Turno *", ["Manhã", "Tarde", "Noite", "Administrativo"])
    setor = st.text_input("Setor *", placeholder="Ex: Manutenção Mecânica")

st.markdown("### 📝 Detalhamento")

descricao = st.text_area("Descrição da Ocorrência *", height=120, placeholder="Descreva detalhadamente o que aconteceu...")
analise_causa = st.text_area("Análise da Causa Raiz *", height=120, placeholder="Use método 5 Porquês, Ishikawa, etc...")
acoes_corretivas = st.text_area("Ações Corretivas *", height=100, placeholder="O que foi feito para corrigir imediatamente...")
acoes_preventivas = st.text_area("Ações Preventivas *", height=100, placeholder="O que será feito para evitar recorrência...")

st.markdown("---")

col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
with col_btn2:
    if st.button("🔄 Gerar PDF do RCA", type="primary", use_container_width=True):
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

            with st.spinner("Gerando PDF..."):
                pdf_buffer = gerar_pdf_mom(dados)

            st.success("✅ PDF gerado com sucesso!")

            st.download_button(
                label="📥 Baixar PDF",
                data=pdf_buffer,
                file_name=f"RCA_{num_mom}_{data_ocorrencia.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )