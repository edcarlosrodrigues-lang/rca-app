import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from datetime import datetime
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image

st.set_page_config(page_title="AQF Industrial", layout="wide", page_icon="🔧")

if 'historico_mom' not in st.session_state:
    st.session_state.historico_mom = []

st.markdown("""
<style>
.stApp { background-color: #F5F5F5; }
.header-box { background: #1B3A4B; padding: 25px; border-radius: 8px; margin-bottom: 20px; }
.header-title { color: #FF8C00; font-size: 32px; font-weight: bold; margin: 0; }
.header-subtitle { color: #D0D0D0; font-size: 13px; margin: 8px 0 0 0; }
.metric-card { background-color: #1A1A1A; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #FF8C00; }
.metric-value { color: #FF8C00; font-size: 36px; font-weight: bold; margin: 0; }
.metric-label { color: #B0B0B0; font-size: 11px; text-transform: uppercase; margin: 5px 0 0 0; letter-spacing: 0.5px; }
.stTabs [data-baseweb="tab-list"] { background-color: #2D2D2D; border-radius: 6px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #B0B0B0; background-color: transparent; border-radius: 4px; padding: 8px 16px; }
.stTabs [aria-selected="true"] { background-color: #FF8C00!important; color: white!important; }
.stTextInput input,.stSelectbox select,.stDateInput input,.stTextArea textarea { background-color: white!important; color: #333!important; border: 1px solid #D0D0D0!important; }
 label { color: #FF8C00!important; font-weight: 600!important; font-size: 13px!important; }
 h3, h4 { color: #FF8C00!important; border-bottom: 2px solid #FF8C00; padding-bottom: 8px; font-weight: 600; }
.stDataFrame { background-color: white; }
.stRadio > label { color: #333!important; }
.stButton button { background-color: #FF8C00; color: white; border: none; font-weight: 600; }
.stButton button:hover { background-color: #E67E00; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <p class="header-title">🔧 AQF INDUSTRIAL</p>
    <p class="header-subtitle">Análise de Causa Raiz - Manufatura & Falhas Industriais</p>
</div>
""", unsafe_allow_html=True)

total_registros = len(st.session_state.historico_mom)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><p class="metric-value">{total_registros}</p><p class="metric-label">Total de RCAs</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><p class="metric-value">0</p><p class="metric-label">Abertos</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><p class="metric-value">0</p><p class="metric-label">Em Andamento</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><p class="metric-value">0</p><p class="metric-label">Concluídos</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["➕ NOVO RCA", "📋 REGISTROS", "📊 DASHBOARD", "📖 GUIA"])

def criar_pdf_mom(data, num_analise, area, maquina, tag, nota_tec, equipamento_parado,
                  classificacao, hrs_parada, hrs_manut, efeito_geral, manutentor1, turno1, o_que, onde,
                  quando, quem, qual, como, quanto, acoes, maquina_4m, material_4m, metodo_4m,
                  mao_obra_4m, efeito_falha_4m, aval1, aval2, aval3, aval4, comp_danificado,
                  buscar_almox, encontrou_almox, perda_regulagem, falha_repetitiva, tempo_quebra,
                  pq1, pq2, pq3, pq4, pq5, causa_raiz, padrao, resp_tecnico, assinatura_img):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=7, leading=9)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontSize=7, leading=9, fontName='Helvetica-Bold')
    y = 1.2

    def draw_table(data, col_widths, y_pos, row_height=0.5):
        t = Table(data, colWidths=[w*cm for w in col_widths])
        t.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica', 7),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))
        t.wrapOn(c, width, height)
        table_height = len(data)*row_height*cm
        t.drawOn(c, 1*cm, height - y_pos*cm - table_height)
        return len(data) * row_height

    def draw_checkbox_table(perguntas, respostas):
        data = []
        for i, p in enumerate(perguntas):
            sim = "X" if respostas[i] == "SIM" else ""
            nao = "X" if respostas[i] == "NÃO" else ""
            data.append([Paragraph(p, style_normal), "SIM", sim, "NÃO", nao])

        t = Table(data, colWidths=[13*cm, 1*cm, 0.5*cm, 1*cm, 0.5*cm])
        t.setStyle(TableStyle([
            ('FONT', (1,0), (-1,-1), 'Helvetica-Bold', 7),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (2,0), (2,-1), 'CENTER'),
            ('ALIGN', (4,0), (4,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        return t

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, height - y*cm, "ANÁLISE DE FALHAS DE MANUTENÇÃO - MOM")
    y += 0.6

    data1 = [[f"DATA: {data.strftime('%d/%m/%Y')}", "USAR SEMPRE PARA PARADAS A PARTIR DE 4 HORAS", f"Nº DE ANÁLISE: {num_analise}"]]
    y += draw_table(data1, [4, 9, 6], y, 0.5)
    y += 0.3

    data2 = [[f"Área: {area}", f"EQUIPAMENTO PARADO? {equipamento_parado}"]]
    y += draw_table(data2, [14, 5], y, 0.5)
    y += 0.3

    data3 = [[f"MÁQUINA: {maquina}", f"TAG: {tag}", f"NOTA TEC.: {nota_tec}"]]
    y += draw_table(data3, [7, 6, 6], y, 0.5)
    y += 0.3

    data4 = [[f"HRS PARADA: {hrs_parada}", f"HRS MANUT: {hrs_manut}", f"EFEITO: {efeito_geral}", f"CLASSIFICAÇÃO: {classificacao}"]]
    y += draw_table(data4, [4, 4, 5, 6], y, 0.5)
    y += 0.3

    data5 = [[f"MANUTENTOR: {manutentor1}", f"TURNO: {turno1}"]]
    y += draw_table(data5, [10, 9], y, 0.5)
    y += 0.6

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1*cm, height - y*cm, "Descrição do Problema - Análise 5W2H")
    y += 0.5
    data_5w2h = [
        [Paragraph("<b>O quê?</b>", style_bold), Paragraph(o_que or "", style_normal)],
        [Paragraph("<b>Onde?</b>", style_bold), Paragraph(onde or "", style_normal)],
        [Paragraph("<b>Quando?</b>", style_bold), Paragraph(quando or "", style_normal)],
        [Paragraph("<b>Quem?</b>", style_bold), Paragraph(quem or "", style_normal)],
        [Paragraph("<b>Qual?</b>", style_bold), Paragraph(qual or "", style_normal)],
        [Paragraph("<b>Como?</b>", style_bold), Paragraph(como or "", style_normal)],
        [Paragraph("<b>Quanto?</b>", style_bold), Paragraph(quanto or "", style_normal)]
    ]
    t = Table(data_5w2h, colWidths=[3*cm, 15*cm])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.3

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1*cm, height - y*cm, "Ações CORRETIVAS")
    y += 0.5
    data_acoes = [[Paragraph(acoes or "", style_normal)]]
    t = Table(data_acoes, colWidths=[19*cm])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.3

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1*cm, height - y*cm, "Avaliação das ações corretivas")
    y += 0.5
    perguntas = ["O Equipamento voltou a funcionar?", "A Ação foi efetiva?", "Operador foi envolvido?", "O Operador entendeu o problema?"]
    respostas = [aval1, aval2, aval3, aval4]
    t = draw_checkbox_table(perguntas, respostas)
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.3

    if y > 22:
        c.showPage()
        y = 1.2

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1*cm, height - y*cm, "TIPO DA QUEBRA / FALHA")
    y += 0.5

    data_q1 = [
        ["Componente Danificado", "Perda de Regulagem", "Qual o Tempo?"],
        [Paragraph(comp_danificado or "", style_normal), f"Não [{'X' if perda_regulagem=='Não' else ' '}] Sim [{'X' if perda_regulagem=='Sim' else ' '}]", Paragraph(tempo_quebra or "", style_normal)]
    ]
    t = Table(data_q1, colWidths=[6*cm, 4*cm, 9*cm])
    t.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.1

    data_q2 = [
        ["Foi necessário buscar componentes no Almoxarifado?", "Foi encontrado o componente no Almoxarifado?"],
        [f"Não [{'X' if buscar_almox=='Não' else ' '}] Sim [{'X' if buscar_almox=='Sim' else ' '}]",
         f"Não [{'X' if encontrou_almox=='Não' else ' '}] Sim [{'X' if encontrou_almox=='Sim' else ' '}]"]
    ]
    t = Table(data_q2, colWidths=[9.5*cm, 9.5*cm])
    t.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.1

    data_q3 = [["Falha Repetitiva:", f"Não [{'X' if falha_repetitiva=='Não' else ' '}] Sim [{'X' if falha_repetitiva=='Sim' else ' '}]"]]
    t = Table(data_q3, colWidths=[3*cm, 16*cm])
    t.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.3

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1*cm, height - y*cm, "Análise dos 5 Porquês")
    y += 0.5

    data_5pq = [["CAUSA Nº:", ""]]
    porques = [
        [Paragraph("<b>Por quê 1?</b>", style_bold), Paragraph(pq1 or "", style_normal)],
        [Paragraph("<b>Por quê 2?</b>", style_bold), Paragraph(pq2 or "", style_normal)],
        [Paragraph("<b>Por quê 3?</b>", style_bold), Paragraph(pq3 or "", style_normal)],
        [Paragraph("<b>Por quê 4?</b>", style_bold), Paragraph(pq4 or "", style_normal)],
        [Paragraph("<b>Por quê 5?</b>", style_bold), Paragraph(pq5 or "", style_normal)],
        [Paragraph("<b>C. RAIZ:</b>", style_bold), Paragraph(causa_raiz or "", style_normal)],
        [Paragraph("<b>PADRÃO:</b>", style_bold), Paragraph(padrao or "", style_normal)]
    ]
    data_5pq.extend(porques)

    t = Table(data_5pq, colWidths=[2*cm, 17*cm])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.3

    if y > 18:
        c.showPage()
        y = 1.2

    c.setFont("Helvetica-Bold", 9)
    c.drawString(1*cm, height - y*cm, "Análise de CAUSA e EFEITO (4M)")
    y += 0.5

    def limpa_num(texto):
        linhas = []
        for linha in (texto or "").split('\n'):
            if linha.strip():
                linhas.append(linha)
        return linhas

    maquina_linhas = limpa_num(maquina_4m)
    material_linhas = limpa_num(material_4m)
    metodo_linhas = limpa_num(metodo_4m)
    mao_obra_linhas = limpa_num(mao_obra_4m)

    while len(maquina_linhas) < 4: maquina_linhas.append("")
    while len(material_linhas) < 4: material_linhas.append("")
    while len(metodo_linhas) < 4: metodo_linhas.append("")
    while len(mao_obra_linhas) < 4: mao_obra_linhas.append("")

    data_ishikawa = [
        [Paragraph("<b>MÉTODO</b>", style_bold), "", Paragraph("<b>MÁQUINA</b>", style_bold), "", Paragraph("<b>Efeito da Falha/Defeito</b>", style_bold)],
        [Paragraph(metodo_linhas[0], style_normal), "", Paragraph(maquina_linhas[0], style_normal), "", Paragraph(efeito_falha_4m or "", style_normal)],
        [Paragraph(metodo_linhas[1], style_normal), "", Paragraph(maquina_linhas[1], style_normal), "", ""],
        [Paragraph(metodo_linhas[2], style_normal), "", Paragraph(maquina_linhas[2], style_normal), "", ""],
        [Paragraph(metodo_linhas[3], style_normal), "", Paragraph(maquina_linhas[3], style_normal), "", ""],
        [Paragraph("<b>MÃO DE OBRA</b>", style_bold), "", Paragraph("<b>MATERIAL</b>", style_bold), "", ""],
        [Paragraph(mao_obra_linhas[0], style_normal), "", Paragraph(material_linhas[0], style_normal), "", ""],
        [Paragraph(mao_obra_linhas[1], style_normal), "", Paragraph(material_linhas[1], style_normal), "", ""],
        [Paragraph(mao_obra_linhas[2], style_normal), "", Paragraph(material_linhas[2], style_normal), "", ""],
        [Paragraph(mao_obra_linhas[3], style_normal), "", Paragraph(material_linhas[3], style_normal), "", ""],
    ]

    t = Table(data_ishikawa, colWidths=[4.5*cm, 0.5*cm, 4.5*cm, 0.5*cm, 9*cm])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (0,4), 0.5, colors.black),
        ('GRID', (2,0), (2,4), 0.5, colors.black),
        ('GRID', (0,5), (0,9), 0.5, colors.black),
        ('GRID', (2,5), (2,9), 0.5, colors.black),
        ('SPAN', (4,0), (4,9)),
        ('BOX', (4,0), (4,9), 0.5, colors.black),
        ('BOX', (0,0), (3,9), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (4,0), (4,0), 'CENTER'),
        ('VALIGN', (4,0), (4,0), 'MIDDLE'),
        ('VALIGN', (4,1), (4,1), 'TOP'),
    ]))
    t.wrapOn(c, width, height)
    table_h = t._height
    t.drawOn(c, 1*cm, height - y*cm - table_h)
    y += (table_h/cm) + 0.5

    c.setFont("Helvetica", 6)
    c.drawString(1*cm, height - y*cm, "*Circular as Causas priorizadas")
    y += 2.0

    c.setFont("Helvetica-Bold", 8)
    c.drawString(1*cm, height - y*cm, "RESPONSÁVEL TÉCNICO:")
    y += 0.5
    c.setFont("Helvetica", 8)
    c.drawString(1*cm, height - y*cm, f"{resp_tecnico or ''}")
    y += 0.5

    if assinatura_img is not None:
        img_buffer = BytesIO()
        assinatura_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        c.drawImage(img_reader, 1*cm, height - y*cm - 2*cm, width=6*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
        y += 2.2
    else:
        c.line(1*cm, height - y*cm, 9*cm, height - y*cm)
        y += 0.5

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

with tab1:
    st.markdown("### ANÁLISE DE FALHAS DE MANUTENÇÃO - MOM")

    with st.form("form_mom"):
        st.markdown("#### Dados Gerais")
        col1, col2 = st.columns(2)
        data = col1.date_input("Data", format="DD/MM/YYYY")
        num_analise = col2.text_input("Nº de Análise de Falhas", value="MOM-001")

        area = st.selectbox("Área", ["RT23 ENVASE", "RT23 FABRICAÇÃO", "CORNER KICK", "RT23 ESTEIRAS", "RT23 ROBOS",
                                     "RT1 AEROSOL", "RT1 COSMÉTICOS", "RT1 BLOCOS", "UTILIDADES", "OUTROS"])

        col1, col2, col3 = st.columns(3)
        maquina = col1.text_input("Máquina")
        tag = col2.text_input("TAG")
        nota_tec = col3.text_input("NOTA TEC.")

        col1, col2 = st.columns(2)
        equipamento_parado = col1.radio("Equipamento Parado?", ["SIM", "NÃO"], horizontal=True)
        classificacao = col2.radio("Classificação do Evento", ["FALHA", "DEFEITO"], horizontal=True)

        col1, col2, col3 = st.columns(3)
        hrs_parada = col1.text_input("HRS PARADA EGA")
        hrs_manut = col2.text_input("HRS MANUTENÇÃO")
        efeito_geral = col3.text_input("EFEITO")

        col1, col2 = st.columns(2)
        manutentor1 = col1.text_input("Manutentor 1")
        turno1 = col2.selectbox("Turno", ["1º Turno", "2º Turno", "3º Turno"])

        st.markdown("#### Descrição do Problema - Análise 5W2H")
        o_que = st.text_area("O quê? (What?)")
        onde = st.text_area("Onde? (Where?)")
        quando = st.text_area("Quando? (When?)")
        quem = st.text_area("Quem? (Who?)")
        qual = st.text_area("Qual? (Which?)")
        como = st.text_area("Como? (How?)")
        quanto = st.text_area("Quanto? (How Much?)")

        st.markdown("#### Ações CORRETIVAS")
        acoes = st.text_area("Descreva as ações corretivas")

        st.markdown("#### Avaliação das Ações Corretivas")
        col1, col2 = st.columns(2)
        aval1 = col1.radio("O Equipamento voltou a funcionar?", ["SIM", "NÃO", "N/A"], horizontal=True)
        aval2 = col2.radio("A Ação foi efetiva?", ["SIM", "NÃO", "N/A"], horizontal=True)
        col3, col4 = st.columns(2)
        aval3 = col3.radio("Operador foi envolvido?", ["SIM", "NÃO", "N/A"], horizontal=True)
        aval4 = col4.radio("O Operador entendeu o problema?", ["SIM", "NÃO", "N/A"], horizontal=True)

        st.markdown("#### TIPO DA QUEBRA / FALHA")
        comp_danificado = st.text_input("Componente Danificado")
        col1, col2, col3 = st.columns(3)
        buscar_almox = col1.radio("Foi necessário buscar componentes no Almoxarifado?", ["Não", "Sim"], horizontal=True)
        encontrou_almox = col2.radio("Foi encontrado o componente no Almoxarifado?", ["Não", "Sim"], horizontal=True)
        falha_repetitiva = col3.radio("Falha Repetitiva:", ["Não", "Sim"], horizontal=True)
        col1, col2 = st.columns(2)
        perda_regulagem = col1.radio("Perda de Regulagem", ["Não", "Sim"], horizontal=True)
        tempo_quebra = col2.text_input("Qual o Tempo?")

        st.markdown("#### Análise dos 5 Porquês")
        pq1 = st.text_input("Por quê 1?")
        pq2 = st.text_input("Por quê 2?")
        pq3 = st.text_input("Por quê 3?")
        pq4 = st.text_input("Por quê 4?")
        pq5 = st.text_input("Por quê 5?")
        causa_raiz = st.text_input("CAUSA RAIZ")
        padrao = st.text_input("PADRÃO")

        st.markdown("#### Análise de CAUSA e EFEITO (4M)")
        st.info("💡 Preencha os códigos das causas. Ex: 01-Desgaste")
        col1, col2 = st.columns(2)
        maquina_4m = col1.text_area("Máquina", "01-Desgaste\n02-Folga\n03\n04")
        material_4m = col2.text_area("Material", "05-Vedação ressecada\n06\n07\n08")
        col3, col4 = st.columns(2)
        metodo_4m = col3.text_area("Método", "09-Falta preventiva\n10\n11\n12")
        mao_obra_4m = col4.text_area("Mão de Obra", "13-Falta treinamento\n14\n15\n16")

        efeito_falha_4m = st.text_input("Efeito da Falha/Defeito")

        st.markdown("#### Responsável Técnico")
        resp_tecnico = st.text_input("Nome do Responsável Técnico")

        enviado = st.form_submit_button("Gerar PDF da Análise", use_container_width=True)

    st.markdown("#### Assinatura Digital do Responsável")
    st.caption("Desenhe sua assinatura abaixo com o mouse ou dedo")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="canvas_assinatura"
    )

    if enviado:
        if not num_analise:
            st.error("⚠️ Preenche o 'Nº de Análise de Falhas' pra gerar o PDF!")
        else:
            assinatura_img = None
            if canvas_result.image_data is not None:
                img_array = canvas_result.image_data.astype('uint8')
                assinatura_img = Image.fromarray(img_array, 'RGBA')
                datas = assinatura_img.getdata()
                newData = []
                for item in datas:
                    if item[0] == 255 and item[1] == 255 and item[2] == 255:
                        newData.append((255, 255, 255, 0))
                    else:
                        newData.append(item)
                assinatura_img.putdata(newData)

            registro = {
                "Data": data.strftime('%d/%m/%Y'),
                "Nº Análise": num_analise,
                "Área": area,
                "Máquina": maquina,
                "TAG": tag,
                "Equipamento Parado": equipamento_parado,
                "Classificação": classificacao,
                "Manutentor": manutentor1,
                "Turno": turno1,
                "HRS Parada": hrs_parada
            }
            st.session_state.historico_mom.append(registro)

            pdf = criar_pdf_mom(data, num_analise, area, maquina, tag, nota_tec,
                               equipamento_parado, classificacao, hrs_parada, hrs_manut, efeito_geral,
                               manutentor1, turno1, o_que, onde, quando, quem, qual, como, quanto,
                               acoes, maquina_4m, material_4m, metodo_4m, mao_obra_4m, efeito_falha_4m,
                               aval1, aval2, aval3, aval4, comp_danificado, buscar_almox, encontrou_almox,
                               perda_regulagem, falha_repetitiva, tempo_quebra, pq1, pq2, pq3, pq4, pq5,
                               causa_raiz, padrao, resp_tecnico, assinatura_img)

            st.success("✅ PDF gerado com assinatura digital!")
            st.download_button(
                label="📄 Baixar PDF - Análise MOM",
                data=pdf,
                file_name=f"MOM_{num_analise}_{data.strftime('%d%m%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

with tab2:
    st.markdown("### 📋 REGISTROS DE ANÁLISES MOM")

    if st.session_state.historico_mom:
        col1, col2 = st.columns([3,1])
        with col1:
            st.markdown(f"**Total de registros: {len(st.session_state.historico_mom)}**")
        with col2:
            if st.button("🗑️ Limpar Tudo", type="secondary", use_container_width=True):
                st.session_state.historico_mom = []
                st.rerun()

        st.dataframe(
            st.session_state.historico_mom,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data": st.column_config.TextColumn("Data", width="small"),
                "Nº Análise": st.column_config.TextColumn("Nº Análise", width="small"),
                "Área": st.column_config.TextColumn("Área", width="medium"),
                "Máquina": st.column_config.TextColumn("Máquina", width="medium"),
            }
        )
    else:
        st.info("📭 Nenhuma análise MOM registrada ainda. Gere um PDF na aba 'NOVO RCA' para começar.")

with tab3:
    st.markdown("### 📊 DASHBOARD")
    st.info("🚧 Dashboard em desenvolvimento - aqui vão entrar gráficos de falhas por área, tempo médio, etc")

with tab4:
    st.markdown("### 📖 GUIA")
    st.info("🚧 Guia em desenvolvimento - instruções de preenchimento do MOM")