import streamlit as st
import pandas as pd
import requests
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SofaScout Pro", page_icon="⚽", layout="wide")

# Estilo CSS para tornar a interface mais bonita
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

def obter_json(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def organizar_stats_jogador(stats_dict):
    mapa = {
        "goals": "Golos", "expectedG": "xG", "totalShot": "Remates",
        "shotOnTarget": "No Alvo", "goalAssist": "Assist.", "expectedA": "xA",
        "keyPass": "Passes Decisivos", "accuratePass": "Passes Certos",
        "totalPass": "Passes Totais", "rating": "Nota"
    }
    return {mapa[k]: (round(v, 2) if isinstance(v, float) else v) for k, v in stats_dict.items() if k in mapa}

# --- INTERFACE ---
st.title("⚽ SofaScout Advanced Analytics")

with st.sidebar:
    st.header("🔎 Pesquisa")
    url_input = st.text_input("Link do Jogo:", placeholder="Cole o URL aqui...")
    processar = st.button("Analisar Partida")

if processar and url_input:
    try:
        match_id = url_input.split(':')[-1] if ':' in url_input else url_input.strip().split('/')[-1]
        
        # 2. CHAMADAS DE API
        event_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}")
        stats_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}/statistics")
        lineup_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}/lineups")

        if not event_data:
            st.error("Não foi possível encontrar o jogo. Verifique o link.")
        else:
            # NOMES DAS EQUIPAS
            casa_nome = event_data['event']['homeTeam']['name']
            fora_nome = event_data['event']['awayTeam']['name']
            placar_casa = event_data['event']['homeScore'].get('display', 0)
            placar_fora = event_data['event']['awayScore'].get('display', 0)

            # CABEÇALHO DO JOGO
            st.markdown(f"### {casa_nome} {placar_casa} - {placar_fora} {fora_nome}")
            
            # INFO DO JOGO (Estádio, Árbitro, Torneio)
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("🏆 Torneio", event_data['event']['tournament']['name'])
            with col_info2:
                st.metric("🏟️ Estádio", event_data['event'].get('venue', {}).get('name', 'N/A'))
            with col_info3:
                st.metric("⚖️ Árbitro", event_data['event'].get('referee', {}).get('name', 'N/A'))

            # ABAS PARA ORGANIZAÇÃO
            aba1, aba2 = st.tabs(["📊 Estatísticas do Jogo", "🏃 Performance Individual"])

            # ABA 1: ESTATÍSTICAS GERAIS
            with aba1:
                if stats_data and 'statistics' in stats_data:
                    # Lista para acumular todos os dados para o Excel
                    lista_excel = []
                    
                    for grupo in stats_data['statistics'][0]['groups']:
                        st.write(f"#### {grupo['groupName']}")
                        stats_list = []
                        for item in grupo['statisticsItems']:
                            dados_linha = {
                                "Métrica": item['name'],
                                casa_nome: item['home'],
                                fora_nome: item['away']
                            }
                            stats_list.append(dados_linha)
                            # Adicionamos também à lista que irá para o Excel (com a info do grupo)
                            lista_excel.append({"Grupo": grupo['groupName'], **dados_linha})
                        
                        st.table(pd.DataFrame(stats_list))
                    
                    # Botão para baixar as estatísticas da Aba 1 em Excel
                    df_excel = pd.DataFrame(lista_excel)
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_excel.to_excel(writer, index=False, sheet_name='Stats Jogo')
                    
                    st.download_button(
                        label="📥 Baixar Estatísticas do Jogo (Excel)",
                        data=buffer.getvalue(),
                        file_name=f"stats_jogo_{casa_nome}_{fora_nome}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                else:
                    st.warning("Estatísticas gerais indisponíveis para este jogo.")

            # ABA 2: JOGADORES
            with aba2:
                col_c, col_f = st.columns(2)
                for i, lado in enumerate(['home', 'away']):
                    nome_atua = casa_nome if lado == 'home' else fora_nome
                    jogadores = []
                    for j in lineup_data.get(lado, {}).get('players', []):
                        if j.get('statistics'):
                            info = {"Jogador": j['player']['name'], "Pos": j['player']['position']}
                            info.update(organizar_stats_jogador(j['statistics']))
                            jogadores.append(info)
                    
                    df = pd.DataFrame(jogadores).fillna(0)
                    with (col_c if i == 0 else col_f):
                        st.subheader(f"🛡️ {nome_atua}")
                        st.dataframe(df, hide_index=True)
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(f"Baixar CSV {nome_atua}", csv, f"{nome_atua}.csv")

            st.success("Dados atualizados!")

    except Exception as e:
        st.error(f"Erro: {e}")
