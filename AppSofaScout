import streamlit as st
import pandas as pd
import requests

# 1. Configuração da Página
st.set_page_config(page_title="SofaScout Pro", page_icon="⚽", layout="wide")

st.title("⚽ SofaScout: Análise Detalhada de Jogadores")
st.markdown("Insira o link do jogo do SofaScore para extrair todas as métricas dos atletas.")

# 2. Sidebar para Input
with st.sidebar:
    st.header("Configurações")
    url_input = st.text_input("Link do Jogo:", placeholder="https://www.sofascore.com/...")
    processar = st.button("Extrair Estatísticas")

# Função para limpar e organizar os dados
def organizar_stats(stats_dict):
    # Tradução das chaves técnicas para nomes amigáveis
    mapa_nomes = {
        "goals": "Golos",
        "expectedG": "xG (Golos Esperados)",
        "totalShot": "Remates",
        "shotOnTarget": "Remates à Baliza",
        "accuratePass": "Passes Certos",
        "totalPass": "Passes Totais",
        "keyPass": "Passes Decisivos",
        "expectedA": "xA (Assist. Esperadas)",
        "bigChanceCreated": "Grandes Chances Criadas",
        "tackle": "Desarmes",
        "interceptionWon": "Interceções",
        "groundDuelWon": "Duelos Chão Ganhos",
        "aerialDuelWon": "Duelos Aéreos Ganhos",
        "rating": "Nota SofaScore"
    }
    
    dados_limpos = {}
    for chave, valor in stats_dict.items():
        if chave in mapa_nomes:
            nome_pt = mapa_nomes[chave]
            # Arredondar valores decimais
            dados_limpos[nome_pt] = round(valor, 2) if isinstance(valor, float) else valor
            
    return dados_limpos

# 3. Lógica de Execução
if processar and url_input:
    try:
        match_id = url_input.split(':')[-1]
        api_url = f"https://www.sofascore.com/api/v1/event/{match_id}/lineups"
        
        # Fingir ser um browser para a API responder na web
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(api_url, headers=headers)
        dados = response.json()

        col1, col2 = st.columns(2)

        for i, lado in enumerate(['home', 'away']):
            equipa_nome = dados[lado]['team']['name']
            jogadores_lista = []

            for j in dados[lado]['players']:
                if j.get('statistics'):
                    info = {"Jogador": j['player']['name']}
                    # Adiciona as estatísticas limpas ao dicionário do jogador
                    info.update(organizar_stats(j['statistics']))
                    jogadores_lista.append(info)

            df = pd.DataFrame(jogadores_lista).fillna(0)
            
            with (col1 if i == 0 else col2):
                st.subheader(f"🛡️ {equipa_nome}")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Botão para baixar Excel desta equipa específica
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(f"Baixar Dados - {equipa_nome}", csv, f"{equipa_nome}.csv", "text/csv")

    except Exception as e:
        st.error(f"Erro ao processar: Verifique se o link está correto.")
