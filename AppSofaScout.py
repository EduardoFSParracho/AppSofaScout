import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SofaScout Pro", page_icon="⚽", layout="wide")

st.title("⚽ SofaScout: Estatísticas Avançadas")
st.markdown("Analise o desempenho individual de cada jogador em segundos.")

# 2. FUNÇÃO DE LIMPEZA E ORGANIZAÇÃO
def organizar_stats(stats_dict):
    # Dicionário de tradução (Técnico -> Português)
    mapa_nomes = {
        "goals": "Golos",
        "expectedG": "xG (Golos Esperados)",
        "totalShot": "Remates",
        "shotOnTarget": "No Alvo",
        "blockedShot": "Remates Bloqueados",
        "goalAssist": "Assistências",
        "expectedA": "xA (Assist. Esperadas)",
        "keyPass": "Passes Decisivos",
        "accuratePass": "Passes Certos",
        "totalPass": "Passes Totais",
        "accurateOppositionHalfPass": "Passes Campo Adv (Certos)",
        "totalOppositionHalfPass": "Passes Campo Adv (Totais)",
        "tackle": "Desarmes",
        "interceptionWon": "Interceções",
        "groundDuelWon": "Duelos Chão Ganhos",
        "aerialDuelWon": "Duelos Ar Ganhos",
        "rating": "Nota"
    }
    
    dados_limpos = {}
    for chave, nome_pt in mapa_nomes.items():
        if chave in stats_dict:
            valor = stats_dict[chave]
            # Arredondar valores decimais (xG e xA)
            dados_limpos[nome_pt] = round(valor, 2) if isinstance(valor, float) else valor
            
    return dados_limpos

# 3. INTERFACE LATERAL (SIDEBAR)
with st.sidebar:
    st.header("Configurações")
    url_input = st.text_input("Link do Jogo do SofaScore:", placeholder="https://www.sofascore.com/...")
    st.info("Dica: Cole o link completo da partida.")
    processar = st.button("Extrair Dados")

# 4. LÓGICA DE EXTRAÇÃO
if processar and url_input:
    try:
        # Extrair ID de forma robusta
        if ':' in url_input:
            match_id = url_input.split(':')[-1]
        else:
            match_id = url_input.strip().split('/')[-1]

        api_url = f"https://www.sofascore.com/api/v1/event/{match_id}/lineups"
        
        # Headers para evitar Erro 403 (Proibido)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.sofascore.com/",
            "Accept-Language": "pt-PT,pt;q=0.9"
        }
        
        with st.spinner("A consultar a base de dados do SofaScore..."):
            response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            col1, col2 = st.columns(2)
            
            for i, lado in enumerate(['home', 'away']):
                if lado in dados:
                    equipa_nome = dados[lado].get('team', {}).get('name', lado.upper())
                    jogadores_lista = []
                    
                    for j in dados[lado].get('players', []):
                        if j.get('statistics'):
                            # Dados base do jogador
                            info = {
                                "Jogador": j['player']['name'],
                                "Pos": j['player']['position']
                            }
                            # Adicionar as métricas estatísticas
                            info.update(organizar_stats(j['statistics']))
                            jogadores_lista.append(info)
                    
                    if jogadores_lista:
                        df = pd.DataFrame(jogadores_lista).fillna(0)
                        
                        # Mostrar na coluna correspondente
                        with (col1 if i == 0 else col2):
                            st.subheader(f"🛡️ {equipa_nome}")
                            # Criar a tabela interativa
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            # Botão de Exportação
                            csv = df.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                label=f"Baixar Excel ({equipa_nome})",
                                data=csv,
                                file_name=f"stats_{equipa_nome}.csv",
                                mime="text/csv"
                            )
            st.success("Extração finalizada!")
        else:
            st.error(f"Erro ao aceder ao site (Código: {response.status_code}). O SofaScore pode estar a proteger os dados.")

    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")

elif processar and not url_input:
    st.warning("Por favor, introduza um link válido primeiro.")
