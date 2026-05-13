from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime

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
        spaceAfter=0,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=22
    )
    
    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    style_secao = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.white,
        backColor=cor_primaria,
        spaceBefore=15,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        leftIndent=6,
        rightIndent=0,
        borderPadding=5
    )
    
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # EXTRAÇÃO DOS DADOS
    num_mom = dados_mom.get('num_mom', '')
    data_ocorrencia = dados_mom.get('data_ocorrencia')
    area = dados_mom.get('area', '')
    turno = dados_mom.get('turno', '')
    equipamento = dados_mom.get('equipamento', '')
    hora_ocorrencia = dados_mom.get('hora_ocorrencia')
    responsavel = dados_mom.get('responsavel', '')
    o_que = dados_mom.get('o_que', '')
    onde = dados_mom.get('onde', '')
    quando = dados_mom.get('quando', '')
    como = dados_mom.get('como', '')
    quem = dados_mom.get('quem', '')
    
    # CABEÇALHO
    elements.append(Paragraph("<b>RELATÓRIO DE ANÁLISE DE FALHAS</b>", style_titulo))
    elements.append(Paragraph("Manutenção Operacional", style_subtitulo))
    
    # LINHA DIVISÓRIA
    linha_data = [
        ['', '']
    ]
    linha = Table(linha_data, colWidths=[17*cm])
    linha.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, cor_primaria),
    ]))
    elements.append(linha)
    elements.append(Spacer(1, 0.4*cm))
    
    # DADOS GERAIS
    elements.append(Paragraph("1. DADOS GERAIS", style_secao))
    elements.append(Spacer(1, 0.2*cm))
    
    dados = [
        ['Nº MOM', num_mom, 'DATA DA OCORRÊNCIA', data_ocorrencia.strftime('%d/%m/%Y')],
        ['ÁREA', area, 'TURNO', turno],
        ['EQUIPAMENTO', equipamento, 'HORA', hora_ocorrencia.strftime('%H:%M')],
        ['RESPONSÁVEL', responsavel, '', '']
    ]
    
    t = Table(dados, colWidths=[3.5*cm, 5*cm, 4*cm, 4.5*cm])
    t.setStyle(TableStyle([
        # Cabeçalhos - fundo azul
        ('BACKGROUND', (0, 0), (0, -1), cor_primaria),
        ('BACKGROUND', (2, 0), (2, -1), cor_primaria),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.white),
        # Dados - fundo cinza claro
        ('BACKGROUND', (1, 0), (1, -1), cor_secundaria),
        ('BACKGROUND', (3, 0), (3, -1), cor_secundaria),
        # Fonte
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, cor_borda),
        ('BOX', (0, 0), (-1, -1), 1, cor_primaria),
        # Alinhamento
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(KeepTogether(t))
    elements.append(Spacer(1, 0.5*cm))
    
    # 5W2H
    elements.append(Paragraph("2. DESCRIÇÃO DO PROBLEMA - 5W2H", style_secao))
    elements.append(Spacer(1, 0.2*cm))
    
    w2h = [
        ["O QUÊ?", Paragraph(o_que or '-', style_normal)],
        ["ONDE?", Paragraph(onde or '-', style_normal)],
        ["QUANDO?", Paragraph(quando or '-', style_normal)],
        ["COMO?", Paragraph(como or '-', style_normal)],
        ["QUEM?", Paragraph(quem or '-', style_normal)],
    ]
    t_w2h = Table(w2h, colWidths=[3.5*cm, 13.5*cm])
    t_w2h.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), cor_primaria),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, cor_borda),
        ('BOX', (0, 0), (-1, -1), 1, cor_primaria),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(KeepTogether(t_w2h))
    
    # RODAPÉ
    elements.append(Spacer(1, 1*cm))
    rodape_data = [
        [f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", f"Página 1 de 1"]
    ]
    rodape = Table(rodape_data, colWidths=[8.5*cm, 8.5*cm])
    rodape.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#999999')),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, -1), 1, cor_borda),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(rodape)
    
    # GERA O PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer