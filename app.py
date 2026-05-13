import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from io import BytesIO

# CONFIGURAÇÃO - TEM QUE SER O PRIMEIRO COMANDO ST
st.set_page_config(
    page_title="RCA - Análise de Falhas",
    layout="wide",
    page_icon="📋"
)

# IMPORTS DO REPORTLAB
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def gerar_pdf_mom(dados_mom):
    """
    Gera PDF profissional - Análise de Falhas de Manutenção
    """
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
    
    # PALETA DE CORES PROFISSIONAL
    cor_primaria = colors.HexColor('#1B3448')  # Azul escuro
    cor_secundaria = colors.HexColor('#F5F5F5')  # Cinza claro
    cor_borda = colors.HexColor('#CCCCCC')
    
    # ESTILOS CUSTOMIZADOS
    style_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=cor_primaria,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=cor_primaria,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # CABEÇALHO
    elements.append(Paragraph("RELATÓRIO DE ANÁLISE DE FALHA - RCA", style_titulo))
    elements.append(Paragraph("Minutes of Meeting - MOM", style_subtitulo))
    elements.append(Spacer(1, 0.5*cm))
    
    # TRATAMENTO DE DATA/HORA - EVITA ERRO DO strftime
    data_ocorrencia = dados_mom.get('data_ocorrencia')
    hora_ocorrencia = dados_mom.get('hora_ocorrencia')
    
    data_formatada = data_ocorrencia.strftime('%d/%m/%Y') if data_ocorrencia else 'Não informado'
    hora_formatada = hora_ocorrencia.strftime('%H:%M') if hora_ocorrencia else 'Não informado'
    
    # TABELA DE DADOS PRINCIPAIS
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
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(tabela)
    elements.append(Spacer(1, 1*cm))
    
    # SEÇÕES DE TEXTO
    secoes = [
        ('DESCRIÇÃO DA OCORRÊNCIA', dados_mom.get('descricao', 'Não informado')),
        ('ANÁLISE DA CAUSA RAIZ', dados_mom.get('analise_causa', 'Não informado')),
        ('AÇÕES CORRETIVAS', dados_mom.get('acoes_corretivas', 'Não informado')),
        ('AÇÕES PREVENTIVAS', dados_mom.get('acoes_preventivas', 'Não informado')),
    ]
    
    for titulo, conteudo in secoes:
        elements.append(Paragraph(titulo, style_subtitulo))
        elements.append(Paragraph(conteudo, style_normal))
        elements.append(Spacer(1, 0.5*cm))
    
    # RODAPÉ
    elements.append(Spacer(1, 1*cm))
    data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    elements.append(Paragraph(f"Relatório gerado em {data_geracao}", style_normal))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# INTERFACE STREAMLIT
st.title("📋 Gerador de RCA - Minutes of Meeting")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    num_mom = st.text_input("Nº MOM", placeholder="Ex: 2026-001")
    area = st.text_input("Área", placeholder="Ex: Laminação")
    equipamento = st.text_input("Equipamento", placeholder="Ex: Ponte Rolante 05")
    responsavel = st.text_input("Responsável", placeholder="Ex: João Silva")

with col2:
    data_ocorrencia = st.date_input("Data da Ocorrência", value=date.today())
    hora_ocorrencia = st.time_input("Hora da Ocorrência", value=datetime.now().time())
    turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite", "Administrativo"])
    setor = st.text_input("Setor", placeholder="Ex: Manutenção Mecânica")

st.markdown("---")

descricao = st.text_area("Descrição da Ocorrência", height=100, placeholder="Descreva o que aconteceu...")
analise_causa = st.text_area("Análise da Causa Raiz", height=100, placeholder="Método 5 Porquês, Ishikawa...")
acoes_corretivas = st.text_area("Ações Corretivas", height=100, placeholder="O que foi feito para corrigir...")
acoes_preventivas = st.text_area("Ações Preventivas", height=100, placeholder="O que será feito para não repetir...")

st.markdown("---")

if st.button("🔄 Gerar PDF do RCA", type="primary", use_container_width=True):
    dados = {
        'num_mom': num_mom,
        'area': area,
        'equipamento': equipamento,
        'responsavel': responsavel,
        'data_ocorrencia': data_ocorrencia,
        'hora_ocorrencia': hora_ocorrencia,
        'turno': turno,
        'setor': setor,
        'descricao': descricao,
        'analise_causa': analise_causa,
        'acoes_corretivas': acoes_corretivas,
        'acoes_preventivas': acoes_preventivas,
    }
    
    pdf_buffer = gerar_pdf_mom(dados)
    
    st.success("✅ PDF gerado com sucesso!")
    
    st.download_button(
        label="📥 Baixar PDF",
        data=pdf_buffer,
        file_name=f"RCA_{num_mom}_{data_ocorrencia.strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )