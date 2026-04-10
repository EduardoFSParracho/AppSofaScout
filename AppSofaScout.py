import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURAÇÃO PREMIUM E CSS CUSTOMIZADO
st.set_page_config(page_title="SofaScout PRO | Dashboard", page_icon="⚽", layout="wide")

# Injeção de CSS para transformar o visual
st.markdown("""
    <style>
    /* Fundo e Fonte Global */
    .main { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    
    /* Estilo dos Títulos */
    h1, h2, h3 { color: #1a202c; font-weight: 800; letter-spacing: -0.5px; }
    
    /* Cartões de Métricas (Top KPIs) */
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 700; color: #2d3748; }
    div[data-testid="stMetricLabel"] { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #718096; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border: 1px solid #e2e8f0; }

    /* Estilo das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #ffffff; border-radius: 10px 10px 0 0; padding: 10px 20px; border: 1px solid #e2e8f0; border-bottom: none; color: #4a5568; font-weight: 600; }
    .stTabs [data-baseweb="tab"]:hover { color: #38a169; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #38a169; color: #ffffff; border-color: #38a169; }

    /* Tabelas e Dataframes */
    .stDataFrame { border-radius: 15px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    
    /* Botões */
    .stButton>button { background-color: #38a169; color: #ffffff; border-radius: 10px; padding: 10px 24px; font-weight: 600; border: none; transition: all 0.2s; }
    .stButton>button:hover { background-color: #2f855a; transform: translateY(-1px); }
    
    /* Barra Lateral */
    .css-1cd4c41 { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE SUPORTE (MANTIDAS)
def obter_json(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def organizar_stats_jogador(stats_dict):
    mapa = {
        "goals": "Golos", "expectedG": "xG", "totalShot": "Remates",
        "shotOnTarget": "No Alvo", "goalAssist": "Assist.", "expectedA": "xA",
        "keyPass": "Passes Decisivos", "accuratePass": "Passes Certos",
        "totalPass": "Passes Totais", "rating": "Nota"
    }
    return {mapa[k]: (round(v, 2) if isinstance(v, float) else v) for k, v in stats_dict.items() if k in mapa}

# 3. INTERFACE PRINCIPAL
st.title("⚽ SofaScout PRO | Dashboard de Análise")

with st.sidebar:
    st.header("⚙️ Central de Comando")
    url_input = st.text_input("URL da Partida SofaScore:", placeholder="https://www.sofascore.com/...")
    st.markdown("---")
    processar = st.button("🚀 Gerar Relatório Premium")
    st.markdown("---")
    st.markdown("Desenvolvido para Scouts Profissionais.")

if processar and url_input:
    try:
        match_id = url_input.split(':')[-1] if ':' in url_input else url_input.strip().split('/')[-1]
        
        # Chamadas de API
        event_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}")
        stats_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}/statistics")
        lineup_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}/lineups")

        if event_data:
            casa_n = event_data['event']['homeTeam']['name']
            fora_n = event_data['event']['awayTeam']['name']
            res_c = event_data['event']['homeScore'].get('display', 0)
            res_f = event_data['event']['awayScore'].get('display', 0)

            # --- CABEÇALHO VISUAL (SCOREBOARD) ---
            st.markdown(f"<h1 style='text-align: center; color: #2d3748; font-size: 48px; margin-bottom: 0;'>{res_c} <span style='color:#a0aec0; font-weight:300;'>vs</span> {res_f}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #718096; font-size: 20px; margin-top: 0;'>{casa_n} vs {fora_n}</p>", unsafe_allow_html=True)
            st.markdown("---")

            # --- KEY PERFORMANCE INDICATORS (METRICS) ---
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            
            # Posse de Bola e xG (Precisamos extrair das Stats Gerais)
            posse_c, posse_f = "N/A", "N/A"
            xg_c, xg_f = 0.0, 0.0
            
            if stats_data:
                for grupo in stats_data['statistics'][0]['groups']:
                    for item in grupo['statisticsItems']:
                        if item['name'] == "Ball possession":
                            posse_c, posse_f = item['home'], item['away']
                        if item['name'] == "Expected goals":
                            xg_c, xg_f = item['home'], item['away']

            with col_kpi1: st.metric("🏆 Competição", event_data['event']['tournament']['name'])
            with col_kpi2: st.metric(f"📈 Posse ({casa_n})", f"{posse_c}")
            with col_kpi3: st.metric(f"📈 Posse ({fora_n})", f"{posse_f}")
            with col_kpi4: st.metric("⚖️ xG Total", f"{xg_c:.2f} - {xg_f:.2f}")
            
            st.markdown("---")

            # --- PROCESSAMENTO PARA EXCEL ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # (Lógica de Excel mantida igual para funcionalidade)
                info_j = pd.DataFrame([{"Torneio": event_data['event']['tournament']['name'], "Resultado": f"{casa_n} {res_c}-{res_f} {fora_n}"}])
                info_j.to_excel(writer, sheet_name='Resumo', index=False)

                # --- ABAS VISUAIS ---
                tab_jogo, tab_jogadores = st.tabs(["📊 ESTATÍSTICAS COLETIVAS", "🏃 PERFORMANCE INDIVIDUAL"])

                with tab_jogo:
                    if stats_data:
                        total_stats = []
                        for grupo in stats_data['statistics'][0]['groups']:
                            st.write(f"#### {grupo['groupName']}")
                            items = []
                            for item in grupo['statisticsItems']:
                                d = {"Métrica": item['name'], casa_n: item['home'], fora_n: item['away']}
                                items.append(d)
                                total_stats.append(d)
                            # Usamos st.dataframe para manter a consistência visual
                            st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
                        pd.DataFrame(total_stats).to_excel(writer, sheet_name='Stats Gerais', index=False)

                with tab_jogadores:
                    col_c, col_f = st.columns(2)
                    for i, lado in enumerate(['home', 'away']):
                        nome_e = casa_n if lado == 'home' else fora_n
                        jogadores = []
                        for j in lineup_data.get(lado, {}).get('players', []):
                            if j.get('statistics'):
                                p_info = {"Jogador": j['player']['name'], "Pos": j['player']['position']}
                                p_info.update(organizar_stats_jogador(j['statistics']))
                                jogadores.append(p_info)
                        
                        df_jog = pd.DataFrame(jogadores).fillna(0)
                        df_jog.to_excel(writer, sheet_name=f'Jogadores {nome_e[:20]}', index=False)
                        
                        # --- APLICAÇÃO DO HEATMAP (ESTILO PREMIUM) ---
                        # Aplica cor de fundo baseada no valor para Nota e xG
                        styled_df = df_jog.style.background_gradient(cmap='Greens', subset=['Nota', 'xG'], vmin=6.0, vmax=9.0)
                        
                        with (col_c if i == 0 else col_f):
                            st.subheader(f"🛡️ {nome_e}")
                            st.dataframe(styled_df, height=600, use_container_width=True, hide_index=True)

            # --- BOTÃO DE DOWNLOAD NA SIDEBAR (VISUAL DESTACADO) ---
            st.sidebar.markdown("---")
            st.sidebar.download_button(
                label="📥 DESCARREGAR EXCEL COMPLETO",
                data=output.getvalue(),
                file_name=f"Relatorio_{casa_n}_vs_{fora_n}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.sidebar.success("Relatório Excel pronto!")

    except Exception as e:
        st.error(f"Erro Crítico: {e}")
