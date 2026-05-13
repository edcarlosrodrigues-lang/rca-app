import streamlit as st
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
from PIL import Image as PILImage
import numpy as np

st.set_page_config(page_title="AQF Industrial", layout="wide")

if 'historico_mom' not in st.session_state:
    st.session_state.historico_mom = []

st.markdown("""
<style>
.main { background-color: #0E1117; }
.header-box { background: linear-gradient(135deg, #1B3448 0%, #2C5F2D 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }
.stButton button { background-color: #FF8C00; color: white; font-weight: bold; border: none; border-radius: 5px; height: 3rem; }
.stButton button:hover { background-color: #FF6B00; }
  h1, h2, h3 { color: #FF8C00; }
.metric-card { background-color: #1A1A1A; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #FF8C00; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <h1 style='color: white; margin: 0;'>AQF INDUSTRIAL</h1>
    <p style='color: #FF8C00; margin: 0; font-size: 1.2rem;'>Análise de Falhas de Manutenção - MOM</p>
</div>
""", unsafe_allow_html=True)

total_registros = len(st.session_state.historico_mom)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><h3 style="margin:0; color:#FF8C00;">{total_registros}</h3><p style="margin:0; color:#888;">Total MOMs</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h3 style="margin:0; color:#FF8C00;">0</h3><p style="margin:0; color:#888;">Este Mês</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h3 style="margin:0; color:#FF8C00;">0</h3><p style="margin:0; color:#888;">Pendentes</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><h3 style="margin:0; color:#FF8C00;">0</h3><p style="margin:0; color:#888;">Concluídos</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 NOVA ANÁLISE MOM", "📋 HISTÓRICO"])

with tab1:
    st.subheader("1. Dados Gerais")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        data_ocorrencia = st.date_input("Data da Ocorrência")
        turno = st.selectbox("Turno", ["1º Turno", "2º Turno", "3º Turno"])
    with col_b:
        hora_ocorrencia = st.time_input("Hora da Ocorrência")
        area = st.selectbox("Área", ["Produção", "Manutenção", "Qualidade", "Logística", "Utilidades"])
    with col_c:
        num_mom = st.text_input("Nº MOM", value="001")
        responsavel = st.text_input("Responsável pela Análise")

    equipamento = st.text_input("Equipamento / Máquina", placeholder="Ex: Seladora 3M - Linha 2")

    st.divider()
    st.subheader("2. Descrição do Problema - 5W2H")
    col1, col2 = st.columns(2)
    with col1:
        o_que = st.text_area("O QUÊ? (Problema)", height=80)
        onde = st.text_input("ONDE? (Local exato)")
        quando = st.text_input("QUANDO? (Data/Hora específica)")
    with col2:
        como = st.text_area("COMO? (Modo de falha)", height=80)
        quem = st.text_input("QUEM? (Detectou)")

    st.divider()
    st.subheader("3. Análise 5 Porquês")
    pq1 = st.text_input("1º Por quê?")
    pq2 = st.text_input("2º Por quê?")
    pq3 = st.text_input("3º Por quê?")
    pq4 = st.text_input("4º Por quê?")
    pq5 = st.text_input("5º Por quê? (Causa Raiz)")

    st.divider()
    st.subheader("4. Análise 4M")
    col1, col2 = st.columns(2)
    with col1:
        mao_obra = st.text_area("MÃO DE OBRA", height=70)
        material = st.text_area("MATERIAL", height=70)
    with col2:
        maquina = st.text_area("MÁQUINA", height=70)
        metodo = st.text_area("MÉTODO", height=70)

    st.divider()
    st.subheader("5. Plano de Ação")
    acao_corretiva = st.text_area("Ação Corretiva Imediata", height=80)
    acao_preventiva = st.text_area("Ação Preventiva", height=80)
    col_a, col_b = st.columns(2)
    with col_a:
        prazo = st.date_input("Prazo")
    with col_b:
        responsavel_acao = st.text_input("Responsável pela Ação")

    st.divider()
    st.subheader("6. Assinatura do Responsável")
    col_sig1, col_sig2, col_sig3 = st.columns([2,2,1])
    with col_sig1:
        nome_forma = st.text_input("**Nome por extenso**", placeholder="Digite seu nome completo")
    with col_sig2:
        st.markdown("**Assinatura à mão**")
        st.caption("Use o dedo no celular ou mouse no PC")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="assinatura_canvas",
            display_toolbar=True
        )
    with col_sig3:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🗑️ Limpar", use_container_width=True):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("💾 GERAR PDF MOM", use_container_width=True):
        assinatura_vazia = True
        if canvas_result.image_data is not None:
            img_array = canvas_result.image_data.astype('uint8')
            if not np.all(img_array[:,:,0:3] == 255):
                assinatura_vazia = False

        if not o_que or not nome_forma:
            st.error("Preencha 'O QUÊ?' e 'Nome por extenso'!")
        elif assinatura_vazia:
            st.error("Faça a assinatura no campo acima antes de gerar o PDF!")
        else:
            st.session_state.historico_mom.append({
    "Data": data_ocorrencia.strftime('%d/%m/%Y'),
    "MOM": num_mom,
    "Área": area,
    "Equipamento": equipamento,
    "Responsável": nome_forma,
    "Prazo": prazo.strftime('%d/%m/%Y')
})

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            elements = []

            styles = getSampleStyleSheet()
            style_titulo = styles['Title']
            style_titulo.fontSize = 14
            style_titulo.textColor = colors.HexColor('#1B3448')
            style_titulo.spaceAfter = 12
            style_titulo.alignment = 1

            style_secao = styles['Heading2']
            style_secao.fontSize = 11
            style_secao.textColor = colors.white
            style_secao.backColor = colors.HexColor('#FF8C00')
            style_secao.spaceAfter = 6
            style_secao.spaceBefore = 12
            style_secao.leftIndent = 6

            style_normal = styles['Normal']
            style_normal.fontSize = 10

            # CABEÇALHO SEM LOGO
            elements.append(Paragraph("<b>ANÁLISE DE FALHAS DE MANUTENÇÃO - MÉTODO MOM</b>", style_titulo))
            elements.append(Spacer(1, 0.5*cm))

            # DADOS GERAIS
            elements.append(Paragraph("DADOS GERAIS", style_secao))
            dados = [
                ["Nº MOM:", num_mom, "DATA:", data_ocorrencia.strftime('%d/%m/%Y')],
                ["ÁREA:", area, "TURNO:", turno],
                ["EQUIPAMENTO:", equipamento, "HORA:", str(hora_ocorrencia)],
                ["RESPONSÁVEL:", responsavel, "", ""],
            ]
            t = Table(dados, colWidths=[3*cm, 5.5*cm, 2.5*cm, 5.5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1B3448')),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#1B3448')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('TEXTCOLOR', (2, 0), (2, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            elements.append(KeepTogether(t))

            # 5W2H
            elements.append(Paragraph("DESCRIÇÃO DO PROBLEMA - 5W2H", style_secao))
            w2h = [
                ["O QUÊ?", o_que],
                ["ONDE?", onde],
                ["QUANDO?", quando],
                ["COMO?", como],
                ["QUEM?", quem],
            ]
            t_w2h = Table(w2h, colWidths=[3*cm, 13.5*cm])
            t_w2h.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FF8C00')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            elements.append(KeepTogether(t_w2h))

            # 5 PORQUÊS
            elements.append(Paragraph("ANÁLISE DOS 5 PORQUÊS", style_secao))
            porques = [
                ["1º POR QUÊ?", pq1],
                ["2º POR QUÊ?", pq2],
                ["3º POR QUÊ?", pq3],
                ["4º POR QUÊ?", pq4],
                ["5º POR QUÊ? (CAUSA RAIZ)", pq5],
            ]
            t_pq = Table(porques, colWidths=[5*cm, 11.5*cm])
            t_pq.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1B3448')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            elements.append(KeepTogether(t_pq))

            # 4M
            elements.append(Paragraph("ANÁLISE 4M", style_secao))
            m4 = [
                ["MÃO DE OBRA", mao_obra],
                ["MÁQUINA", maquina],
                ["MATERIAL", material],
                ["MÉTODO", metodo],
            ]
            t_4m = Table(m4, colWidths=[4*cm, 12.5*cm])
            t_4m.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FF8C00')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            elements.append(KeepTogether(t_4m))

            # PLANO DE AÇÃO
            elements.append(Paragraph("PLANO DE AÇÃO", style_secao))
            plano = [
                ["AÇÃO CORRETIVA:", acao_corretiva],
                ["AÇÃO PREVENTIVA:", acao_preventiva],
                ["PRAZO:", str(prazo.strftime('%d/%m/%Y')), "RESPONSÁVEL:", responsavel_acao],
            ]
            t_plano = Table(plano, colWidths=[4*cm, 12.5*cm])
            t_plano.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1B3448')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            elements.append(KeepTogether(t_plano))

            # ASSINATURA
            elements.append(Spacer(1, 1*cm))
            elements.append(Paragraph("ASSINATURA DO RESPONSÁVEL", style_secao))
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph(f"<b>Nome:</b> {nome_forma}", style_normal))
            elements.append(Spacer(1, 0.5*cm))

            if not assinatura_vazia:
                img_array = canvas_result.image_data.astype('uint8')
                img_pil = PILImage.fromarray(img_array, 'RGBA')
                datas = img_pil.getdata()
                new_data = []
                for item in datas:
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                img_pil.putdata(new_data)

                img_buffer = BytesIO()
                img_pil.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                img_ass = Image(img_buffer, width=6*cm, height=3*cm)
                elements.append(img_ass)

            elements.append(Paragraph("_" * 40, style_normal))
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}", style_normal))

            doc.build(elements)
            pdf = buffer.getvalue()

            st.success("✅ MOM gerado com sucesso!")
            st.download_button(
                label="📥 BAIXAR PDF",
                data=pdf,
                file_name=f"MOM_{num_mom}_{area}_{data_ocorrencia.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

with tab2:
    st.subheader("Histórico de Análises MOM")
    if st.session_state.historico_mom:
        st.dataframe(st.session_state.historico_mom, use_container_width=True)
    else:
        st.info("Nenhuma análise MOM cadastrada ainda.")