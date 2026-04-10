import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MatchBrief Pro - Analytics", page_icon="⚽", layout="wide")

# Estilo CSS (Fundo e métricas)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# DICIONÁRIO DE TRADUÇÃO PARA ESTATÍSTICAS GERAIS (Aba 1)
def traduzir_metrica(nome_en):
    traducoes = {
        "Ball possession": "Posse de bola",
        "Expected goals": "Golos Esperados (xG)",
        "Big chances": "Grandes oportunidades",
        "Total shots": "Total de remates",
        "Goalkeeper saves": "Defesas do guarda-redes",
        "Corner kicks": "Cantos",
        "Fouls": "Faltas",
        "Passes": "Passes",
        "Tackles": "Desarmes",
        "Free kicks": "Livres",
        "Yellow cards": "Cartões amarelos",
        "Red cards": "Cartões vermelhos",
        "Shots on target": "Remates à baliza",
        "Hit woodwork": "Bolas no poste",
        "Shots off target": "Remates para fora",
        "Blocked shots": "Remates bloqueados",
        "Shots inside box": "Remates dentro da área",
        "Shots outside box": "Remates fora da área",
        "Big chances scored": "Grandes oportunidades marcadas",
        "Big chances missed": "Grandes oportunidades falhadas",
        "Through balls": "Passes em rutura",
        "Touches in penalty area": "Toques na área de penalti",
        "Fouled in final third": "Faltas sofridas no último terço",
        "Offsides": "Foras de jogo",
        "Counter attacks": "Contra-ataques",
        "Accurate passes": "Passes certos",
        "Throw-ins": "Lançamentos de linha lateral",
        "Final third entries": "Entradas no último terço",
        "Final third phase": "Passes no último terço",
        "Long balls": "Bolas longas",
        "Crosses": "Cruzamentos",
        "Duels": "Duelos",
        "Dispossessed": "Perda de posse",
        "Ground duels": "Duelos pelo chão",
        "Aerial duels": "Duelos aéreos",
        "Dribbles": "Fintas/Dribles",
        "Tackles won": "Desarmes ganhos (%)",
        "Total tackles": "Total de desarmes",
        "Interceptions": "Interceções",
        "Recoveries": "Recuperações de bola",
        "Clearances": "Alívios",
        "Errors lead to a shot": "Erros que levaram a remate",
        "Errors lead to a goal": "Erros que levaram a golo",
        "Total saves": "Total de defesas",
        "Goals prevented": "Golos evitados",
        "Big saves": "Defesas difíceis",
        "High claims": "Saídas aos cruzamentos",
        "Punches": "Socos",
        "Goal kicks": "Pontapés de baliza"
    }
    return traducoes.get(nome_en, nome_en)

def obter_json(url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.sofascore.com/",
        "Authority": "api.sofascore.com"
    }
    try:
        session.get("https://www.sofascore.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def organizar_stats_jogador(stats_dict):
    mapa = {
        "rating": "Nota", "minutesPlayed": "Min", "goals": "Golos",
        "expectedGoals": "xG", "totalShot": "Remates", "shotOnTarget": "No Alvo",
        "goalAssist": "Assist.", "expectedAssists": "xA", "keyPass": "Passes Chave",
        "bigChanceCreated": "Grd. Oport. Criadas", "accuratePass": "Passes Certos",
        "totalPass": "Passes Totais", "totalBallCarriesDistance": "Dist. Condução (m)",
        "duelWon": "Duelos Ganhos", "ballRecovery": "Recuperações",
        "interceptionWon": "Interceções", "wonTackle": "Desarmes Ganhos",
        "totalClearance": "Alívios", "saves": "Defesas", "goalsPrevented": "Golos Evitados"
    }
    resultado = {}
    for chave_api, nome_pt in mapa.items():
        valor = stats_dict.get(chave_api, 0)
        resultado[nome_pt] = round(valor, 2) if isinstance(valor, float) else valor
    return resultado

# --- INTERFACE PRINCIPAL ---
st.title("⚽ MatchBrief")

with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.warning("⚠️ Ficheiro 'logo.png' não encontrado.")
    
    st.header("🔎 Pesquisa")
    url_input = st.text_input("Link do Jogo:", placeholder="Cole o URL aqui...")
    processar = st.button("Analisar Partida")

if processar and url_input:
    try:
        match_id = url_input.split(':')[-1] if ':' in url_input else url_input.strip().split('/')[-1]
        
        event_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}")
        stats_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}/statistics")
        lineup_data = obter_json(f"https://www.sofascore.com/api/v1/event/{match_id}/lineups")

        if not event_data:
            st.error("Erro ao aceder aos dados.")
        else:
            event_info = event_data['event']
            casa_nome = event_info['homeTeam']['name']
            fora_nome = event_info['awayTeam']['name']
            placar_casa = event_info['homeScore'].get('display', 0)
            placar_fora = event_info['awayScore'].get('display', 0)

            st.markdown(f"### {casa_nome} {placar_casa} - {placar_fora} {fora_nome}")
            
            aba1, aba2 = st.tabs(["📊 Estatísticas Coletivas", "🏃 Performance Individual (Pro)"])

            with aba1:
                st.markdown("#### 📋 Detalhes da Partida")
                col_i1, col_i2, col_i3, col_i4 = st.columns(4)
                ts = event_info.get('startTimestamp')
                data_hora = datetime.fromtimestamp(ts).strftime('%d/%m/%Y %H:%M') if ts else "N/A"
                
                with col_i1:
                    st.write("**🕒 Data e Hora**"); st.write(data_hora)
                with col_i2:
                    st.write("**🏟️ Estádio**"); st.write(event_info.get('venue', {}).get('name', 'N/A'))
                with col_i3:
                    st.write("**⚖️ Árbitro**"); st.write(event_info.get('referee', {}).get('name', 'N/A'))
                with col_i4:
                    st.write("**📍 Cidade**"); st.write(event_info.get('venue', {}).get('city', {}).get('name', 'N/A'))
                
                st.divider()

                if stats_data and 'statistics' in stats_data:
                    lista_excel = []
                    for grupo in stats_data['statistics'][0]['groups']:
                        st.write(f"#### {grupo['groupName']}")
                        stats_list = []
                        for item in grupo['statisticsItems']:
                            nome_pt = traduzir_metrica(item['name'])
                            dados_linha = {"Métrica": nome_pt, casa_nome: item['home'], fora_nome: item['away']}
                            stats_list.append(dados_linha)
                            lista_excel.append({"Grupo": grupo['groupName'], **dados_linha})
                        st.table(pd.DataFrame(stats_list))
                    
                    df_excel = pd.DataFrame(lista_excel)
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_excel.to_excel(writer, index=False, sheet_name='Stats Jogo')
                    st.download_button("📥 Baixar Excel", buffer.getvalue(), f"stats_{casa_nome}_{fora_nome}.xlsx")

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
                    cols_foco = ["Jogador", "Pos", "Nota", "Golos", "xG", "Assist.", "xA", "Min"]
                    cols_restantes = [c for c in df.columns if c not in cols_foco]
                    df = df[cols_foco + cols_restantes]

                    with (col_c if i == 0 else col_f):
                        st.subheader(f"🛡️ {nome_atua}")
                        st.dataframe(df, hide_index=True, use_container_width=True)
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(f"Baixar CSV {nome_atua}", csv, f"{nome_atua}.csv")

            st.success("Concluído!")
    except Exception as e:
        st.error(f"Erro: {e}")
