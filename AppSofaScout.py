import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SofaScout Pro", page_icon="⚽", layout="wide")

# Estilo CSS para tornar a interface mais bonita
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    /* Alinhamento central para o scoreboard */
    .scoreboard { display: flex; align-items: center; justify-content: center; gap: 20px; }
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
            # DADOS DAS EQUIPAS E PLACAR
            casa = event_data['event']['homeTeam']
            fora = event_data['event']['awayTeam']
            casa_nome, casa_id = casa['name'], casa['id']
            fora_nome, fora_id = fora['name'], fora['id']
            placar_casa = event_data['event']['homeScore'].get('display', 0)
            placar_fora = event_data['event']['awayScore'].get('display', 0)

            # --- SCOREBOARD COM IMAGENS ---
            st.markdown("---")
            col_l1, col_score, col_l2 = st.columns([1, 2, 1])
            
            with col_l1:
                st.image(f"https://sofascore.com/api/v1/team/{casa_id}/image", width=80)
                st.subheader(casa_nome)
                
            with col_score:
                st.markdown(f"<h1 style='text-align: center; font-size: 60px;'>{placar_casa} - {placar_fora}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>{event_data['event']['tournament']['name']}</p>", unsafe_allow_html=True)
                
            with col_l2:
                # Alinhamento manual para o logo da direita
                st.image(f"https://sofascore.com/api/v1/team/{fora_id}/image", width=80)
                st.subheader(fora_nome)
            st.markdown("---")
            
            # INFO DO JOGO (Estádio, Árbitro)
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("🏟️ Estádio", event_data['event'].get('venue', {}).get('name', 'N/A'))
            with col_info2:
                st.metric("⚖️ Árbitro", event_data['event'].get('referee', {}).get('name', 'N/A'))

            # ABAS PARA ORGANIZAÇÃO
            aba1, aba2 = st.tabs(["📊 Estatísticas do Jogo", "🏃 Performance Individual"])

            # ABA 1: ESTATÍSTICAS GERAIS
            with aba1:
                if stats_data and 'statistics' in stats_data:
                    for grupo in stats_data['statistics'][0]['groups']:
                        st.write(f"#### {grupo['groupName']}")
                        stats_list = []
                        for item in grupo['statisticsItems']:
                            stats_list.append({
                                "Métrica": item['name'],
                                casa_nome: item['home'],
                                fora_nome: item['away']
                            })
                        st.table(pd.DataFrame(stats_list))
                else:
                    st.warning("Estatísticas gerais indisponíveis.")

            # ABA 2: JOGADORES (Com nota de destaque)
            with aba2:
                col_c, col_f = st.columns(2)
                for i, lado in enumerate(['home', 'away']):
                    nome_atua = casa_nome if lado == 'home' else fora_nome
                    equipa_id = casa_id if lado == 'home' else fora_id
                    
                    jogadores = []
                    for j in lineup_data.get(lado, {}).get('players', []):
                        if j.get('statistics'):
                            info = {"Jogador": j['player']['name'], "Pos": j['player']['position']}
                            info.update(organizar_stats_jogador(j['statistics']))
                            jogadores.append(info)
                    
                    df = pd.DataFrame(jogadores).fillna(0)
                    
                    with (col_c if i == 0 else col_f):
                        st.image(f"https://sofascore.com/api/v1/team/{equipa_id}/image", width=30)
                        st.subheader(f"{nome_atua}")
                        # Aplicar uma cor suave para destacar as notas altas
                        st.dataframe(df.style.background_gradient(cmap='Greens', subset=['Nota']), use_container_width=True, hide_index=True)
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(f"Exportar {nome_atua}", csv, f"{nome_atua}.csv")

            st.success("Dados atualizados com sucesso!")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
