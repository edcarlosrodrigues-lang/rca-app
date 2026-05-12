import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="AQF Industrial",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
h1, h2, h3 { font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; }

.main-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2rem 2rem 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border-left: 5px solid #f7971e;
}
.main-header h1 { color: #f7971e; font-size: 2.2rem; margin: 0; }
.main-header p  { color: #a8c0cc; margin: 0.3rem 0 0 0; font-size: 0.95rem; }

.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #2d4a6b;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    border-top: 3px solid #f7971e;
}
.metric-card .value { font-family: 'Rajdhani', sans-serif; font-size: 2rem; font-weight: 700; color: #f7971e; }
.metric-card .label { color: #8899aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }

.section-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem; font-weight: 700; color: #f7971e;
    border-bottom: 2px solid #2d4a6b;
    padding-bottom: 0.4rem; margin-bottom: 1rem;
    text-transform: uppercase; letter-spacing: 1px;
}
.why-box {
    background: #0d1b2a; border-left: 4px solid #f7971e;
    border-radius: 0 8px 8px 0; padding: 0.8rem 1rem;
    margin: 0.4rem 0; color: #d0dde8; font-size: 0.95rem;
}
.why-label { font-family: 'Rajdhani', sans-serif; color: #f7971e; font-weight: 700; font-size: 1rem; margin-right: 0.5rem; }
.action-card { background: #0d1b2a; border: 1px solid #2d4a6b; border-radius: 8px; padding: 0.8rem 1rem; margin: 0.4rem 0; }
.badge-open { background:#c0392b; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.75rem; }
.badge-prog { background:#e67e22; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.75rem; }
.badge-done { background:#27ae60; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.75rem; }

.stButton > button {
    background: linear-gradient(90deg, #f7971e, #ffd200);
    color: #0f2027; font-family: 'Rajdhani', sans-serif;
    font-weight: 700; font-size: 1rem; border: none;
    border-radius: 8px; padding: 0.5rem 1.5rem; letter-spacing: 1px;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stDateInput"] label { color: #a8c0cc; font-size: 0.9rem; font-weight: 600; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #0d1b2a; padding: 4px; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { font-family: 'Rajdhani', sans-serif; font-weight: 600; letter-spacing: 1px; color: #8899aa; }
.stTabs [aria-selected="true"] { background: linear-gradient(90deg, #f7971e, #ffd200) !important; color: #0f2027 !important; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "rca_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "registros" not in st.session_state:
    st.session_state.registros = load_data()

st.markdown("""
<div class="main-header">
  <h1>🔧 AQF INDUSTRIAL</h1>
  <p>Análise de Causa Raiz · Manufatura & Falhas Industriais</p>
</div>
""", unsafe_allow_html=True)

total    = len(st.session_state.registros)
abertos  = sum(1 for r in st.session_state.registros if r.get("status") == "Aberto")
em_prog  = sum(1 for r in st.session_state.registros if r.get("status") == "Em andamento")
fechados = sum(1 for r in st.session_state.registros if r.get("status") == "Concluído")

c1, c2, c3, c4 = st.columns(4)
for col, val, lbl in zip([c1,c2,c3,c4],[total,abertos,em_prog,fechados],
                          ["Total de AQFs","Abertos","Em Andamento","Concluídos"]):
    col.markdown(f'<div class="metric-card"><div class="value">{val}</div><div class="label">{lbl}</div></div>',
                 unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["➕  NOVA AQF","📋  REGISTROS","📊  DASHBOARD","📖  GUIA"])

with tab1:
    st.markdown('<div class="section-title">Identificação da Falha</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        titulo      = st.text_input("Título da Ocorrência", placeholder="Ex: Parada de linha – Motor elétrico P-03")
        equipamento = st.text_input("Equipamento / Linha", placeholder="Ex: Motor elétrico P-03")
        area        = st.selectbox("Área", ["Produção","Manutenção","Qualidade","Logística","Utilidades","Outro"])
    with col_b:
        data_ocorr  = st.date_input("Data da Ocorrência", value=datetime.today())
        gravidade   = st.selectbox("Gravidade", ["🔴 Crítica","🟠 Alta","🟡 Média","🟢 Baixa"])
        responsavel = st.text_input("Responsável pela Análise", placeholder="Nome do técnico")

    descricao = st.text_area("Descrição da Falha / Problema", height=100,
                             placeholder="Descreva o que aconteceu, quando, como foi detectado...")

    st.markdown('<div class="section-title" style="margin-top:1.5rem">Metodologia 5 Porquês</div>', unsafe_allow_html=True)
    st.caption("Preencha cada 'Por quê?' aprofundando a causa. Pule os que não se aplicarem.")

    whys = []
    for i in range(1, 6):
        w = st.text_input(f"Por quê {i}?", key=f"why_{i}", placeholder=f"Causa nível {i}...")
        whys.append(w)

    causa_raiz = st.text_area("✅ Causa Raiz Identificada", height=80,
                              placeholder="Resumo da causa raiz final após os 5 Porquês...")

    st.markdown('<div class="section-title" style="margin-top:1.5rem">Plano de Ação</div>', unsafe_allow_html=True)
    st.caption("Adicione as ações corretivas / preventivas.")

    if "acoes" not in st.session_state:
        st.session_state.acoes = [{"acao":"","responsavel":"","prazo":""}]

    def add_acao():
        st.session_state.acoes.append({"acao":"","responsavel":"","prazo":""})

    for idx, acao in enumerate(st.session_state.acoes):
        ca, cb, cc = st.columns([4,2,2])
        st.session_state.acoes[idx]["acao"]        = ca.text_input(f"Ação {idx+1}", value=acao["acao"],       key=f"ac_{idx}")
        st.session_state.acoes[idx]["responsavel"] = cb.text_input("Responsável",  value=acao["responsavel"], key=f"ar_{idx}")
        st.session_state.acoes[idx]["prazo"]       = cc.text_input("Prazo",        value=acao["prazo"],       key=f"ap_{idx}", placeholder="dd/mm/aaaa")

    st.button("＋ Adicionar Ação", on_click=add_acao)
    status = st.selectbox("Status do RCA", ["Aberto","Em andamento","Concluído"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾  SALVAR RCA"):
        if not titulo:
            st.error("Informe o título da ocorrência.")
        else:
            novo = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "titulo": titulo, "equipamento": equipamento, "area": area,
                "data": str(data_ocorr), "gravidade": gravidade, "responsavel": responsavel,
                "descricao": descricao,
                "whys": [w for w in whys if w.strip()],
                "causa_raiz": causa_raiz,
                "acoes": [a for a in st.session_state.acoes if a["acao"].strip()],
                "status": status,
            }
            st.session_state.registros.append(novo)
            save_data(st.session_state.registros)
            st.session_state.acoes = [{"acao":"","responsavel":"","prazo":""}]
            st.success(f"✅ RCA '{titulo}' salvo com sucesso!")
            st.rerun()

with tab2:
    st.markdown('<div class="section-title">Registros de RCA</div>', unsafe_allow_html=True)
    if not st.session_state.registros:
        st.info("Nenhum RCA registrado ainda. Crie o primeiro na aba ➕ NOVO RCA.")
    else:
        filtro_status = st.selectbox("Filtrar por status", ["Todos","Aberto","Em andamento","Concluído"])
        lista = st.session_state.registros
        if filtro_status != "Todos":
            lista = [r for r in lista if r.get("status") == filtro_status]
        for reg in reversed(lista):
            badge_map = {"Aberto":"badge-open","Em andamento":"badge-prog","Concluído":"badge-done"}
            badge_cls = badge_map.get(reg.get("status",""), "badge-open")
            with st.expander(f"🔧 {reg['titulo']}  —  {reg['data']}  |  {reg.get('area','')}"):
                cc1, cc2 = st.columns(2)
                cc1.markdown(f"**Equipamento:** {reg.get('equipamento','—')}")
                cc1.markdown(f"**Responsável:** {reg.get('responsavel','—')}")
                cc1.markdown(f"**Gravidade:** {reg.get('gravidade','—')}")
                cc2.markdown(f"**Status:** <span class='{badge_cls}'>{reg.get('status','')}</span>", unsafe_allow_html=True)
                st.markdown("**Descrição:**")
                st.markdown(f"> {reg.get('descricao','—')}")
                if reg.get("whys"):
                    st.markdown("**5 Porquês:**")
                    for i, w in enumerate(reg["whys"], 1):
                        st.markdown(f'<div class="why-box"><span class="why-label">Por quê {i}:</span>{w}</div>', unsafe_allow_html=True)
                if reg.get("causa_raiz"):
                    st.markdown(f"**✅ Causa Raiz:** {reg['causa_raiz']}")
                if reg.get("acoes"):
                    st.markdown("**Plano de Ação:**")
                    for a in reg["acoes"]:
                        st.markdown(f'<div class="action-card">▸ {a["acao"]} &nbsp;|&nbsp; <b>Resp:</b> {a["responsavel"]} &nbsp;|&nbsp; <b>Prazo:</b> {a["prazo"]}</div>', unsafe_allow_html=True)
                if st.button("🗑 Excluir", key=f"del_{reg['id']}"):
                    st.session_state.registros = [r for r in st.session_state.registros if r["id"] != reg["id"]]
                    save_data(st.session_state.registros)
                    st.rerun()

with tab3:
    st.markdown('<div class="section-title">Dashboard Analítico</div>', unsafe_allow_html=True)
    if not st.session_state.registros:
        st.info("Sem dados para exibir. Crie alguns RCAs primeiro.")
    else:
        df = pd.DataFrame(st.session_state.registros)
        col1, col2 = st.columns(2)
        with col1:
            sc = df["status"].value_counts().reset_index()
            sc.columns = ["Status","Quantidade"]
            fig1 = px.pie(sc, names="Status", values="Quantidade", title="RCAs por Status",
                          color_discrete_sequence=["#c0392b","#e67e22","#27ae60"])
            fig1.update_layout(paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a", font_color="#d0dde8", title_font_family="Rajdhani")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            ac = df["area"].value_counts().reset_index()
            ac.columns = ["Área","Quantidade"]
            fig2 = px.bar(ac, x="Área", y="Quantidade", title="RCAs por Área",
                          color_discrete_sequence=["#f7971e"])
            fig2.update_layout(paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a", font_color="#d0dde8", title_font_family="Rajdhani")
            st.plotly_chart(fig2, use_container_width=True)
        if "gravidade" in df.columns:
            gc = df["gravidade"].value_counts().reset_index()
            gc.columns = ["Gravidade","Quantidade"]
            fig3 = px.bar(gc, x="Gravidade", y="Quantidade", title="RCAs por Gravidade",
                          color_discrete_sequence=["#ffd200","#f7971e","#e67e22","#c0392b"])
            fig3.update_layout(paper_bgcolor="#0d1b2a", plot_bgcolor="#0d1b2a", font_color="#d0dde8", title_font_family="Rajdhani")
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown('<div class="section-title">Tabela Completa</div>', unsafe_allow_html=True)
        cols_show = ["titulo","area","equipamento","data","gravidade","status","responsavel"]
        cols_show = [c for c in cols_show if c in df.columns]
        st.dataframe(df[cols_show], use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv, "rca_export.csv", "text/csv")

with tab4:
    st.markdown('<div class="section-title">Como usar a metodologia 5 Porquês</div>', unsafe_allow_html=True)
    st.markdown("""
A técnica dos **5 Porquês** foi criada por Sakichi Toyoda e popularizada pelo Sistema Toyota de Produção.
O objetivo é **escavar as causas** até chegar na raiz real do problema.

---
### Exemplo Prático

**Problema:** Linha de montagem parou.

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | Por quê a linha parou? | Porque o motor da esteira queimou |
| 2 | Por quê o motor queimou? | Porque superaqueceu |
| 3 | Por quê superaqueceu? | Porque o ventilador estava bloqueado |
| 4 | Por quê o ventilador estava bloqueado? | Porque não havia plano de limpeza |
| 5 | Por quê não havia plano de limpeza? | **Porque não existe procedimento de manutenção preventiva** |

✅ **Causa Raiz:** Ausência de procedimento de manutenção preventiva.

---
### Níveis de Gravidade
| Nível | Critério |
|-------|----------|
| 🔴 Crítica | Risco à segurança, parada total da produção |
| 🟠 Alta | Perda de qualidade ou parada parcial |
| 🟡 Média | Desvio de processo sem parada |
| 🟢 Baixa | Anomalia menor, sem impacto imediato |
""")