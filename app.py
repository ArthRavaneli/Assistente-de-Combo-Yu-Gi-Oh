import streamlit as st
import json
import google.generativeai as genai
import os
from st_clickable_images import clickable_images

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Yu-Gi-Oh! AI", page_icon="🐉", layout="wide")

# --- CSS CORRETIVO (Layout e Zoom) ---
st.markdown("""
    <style>
        /* 1. AUMENTA A MARGEM DO TOPO (Para não comer o texto) */
        .block-container {
            padding-top: 5rem !important; 
            padding-bottom: 5rem;
        }
        /* 2. Centraliza a galeria */
        iframe {
            margin: auto;
            display: block;
        }
        /* 3. Estilo da "Mão" no topo */
        .mao-container {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR CHAVE ---
def carregar_chave_arquivo():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return None

chave_arquivo = carregar_chave_arquivo()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # SLIDER DE ZOOM (Novidade!)
    zoom_nivel = st.slider("🔍 Zoom das Cartas", min_value=80, max_value=300, value=130, step=10)
    
    if chave_arquivo:
        api_key = chave_arquivo
    else:
        api_key = st.text_input("API Key:", type="password")
    
    archetype = st.text_input("Deck:", value="Blue-Eyes White Dragon")
    
    # Inicializa memória
    if 'mao_selecionada' not in st.session_state:
        st.session_state['mao_selecionada'] = []
    if 'galeria_id' not in st.session_state:
        st.session_state['galeria_id'] = 0

    st.divider()
    if st.button("🗑️ Limpar Mão", use_container_width=True):
        st.session_state['mao_selecionada'] = []
        st.rerun()

# --- FUNÇÕES ---
@st.cache_data
def carregar_banco():
    try:
        with open("master_duel_deck.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            dados.sort(key=lambda x: x['nome_pt'])
            return dados
    except: return []

# --- INTERFACE PRINCIPAL ---
st.title("🐉 Galeria de Duelo")

deck_data = carregar_banco()
st.session_state['banco_dados'] = deck_data

if deck_data:
    # 1. MOSTRAR A MÃO SELECIONADA (VISUAL TOPO)
    # Como a galeria de baixo não muda de cor, mostramos a seleção aqui em cima
    if st.session_state['mao_selecionada']:
        st.markdown("### ✋ Sua Mão Atual:")
        
        # Cria colunas para mostrar as cartas selecionadas
        cols = st.columns(len(st.session_state['mao_selecionada']) + 1) # +1 para garantir espaço
        for i, nome_carta in enumerate(st.session_state['mao_selecionada']):
            # Acha a imagem correspondente
            dados_carta = next((c for c in deck_data if c['nome_pt'] == nome_carta), None)
            if dados_carta:
                with cols[i]:
                    st.image(dados_carta['imagem'], width=100)
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state['mao_selecionada'].remove(nome_carta)
                        st.rerun()
        st.divider()

        # Botão de Análise (Só aparece se tiver cartas)
        if st.button("🧠 ANALISAR JOGADA", type="primary", use_container_width=True):
            if not api_key:
                st.error("Faltou a API Key!")
            else:
                with st.spinner("O Dragão Branco está calculando..."):
                    try:
                        # Busca dados completos
                        cartas_objs = [c for c in deck_data if c['nome_pt'] in st.session_state['mao_selecionada']]
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        detalhes = "\n".join([f"- {c['nome_pt']}: {c['efeito']}" for c in cartas_objs])
                        
                        prompt = f"""
                        Atue como Pro Player Yu-Gi-Oh. DECK: {archetype}.
                        MÃO: {', '.join(st.session_state['mao_selecionada'])}
                        DETALHES: {detalhes}
                        OBJETIVO: Combo Turno 1 (Best of 1).
                        REGRAS: 
                        1. Responda em Português. 
                        2. Seja visual (Use setas ->).
                        3. Indique o campo final.
                        """
                        res = model.generate_content(prompt).text
                        st.success("⚡ **Estratégia Encontrada:**")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Erro na IA: {e}")

    # 2. GALERIA DE SELEÇÃO (FICHÁRIO)
    st.markdown("### 📖 Fichário (Clique para adicionar):")
    
    imagens_urls = [c["imagem"] for c in deck_data]
    nomes_cartas = [c["nome_pt"] for c in deck_data]

    clicada = clickable_images(
        imagens_urls, 
        titles=nomes_cartas,
        div_style={
            "display": "flex", 
            "justify-content": "center", 
            "flex-wrap": "wrap", 
            "background-color": "#0e1117", 
            "padding": "10px"
        },
        # O TAMANHO AGORA VEM DO SLIDER DA BARRA LATERAL
        img_style={
            "margin": "5px", 
            "height": f"{zoom_nivel}px", 
            "cursor": "pointer",
            "border-radius": "5px",
            "transition": "transform 0.2s" # Adiciona animação leve ao passar mouse
        },
        key=f"fichario_{st.session_state['galeria_id']}"
    )

    # Lógica do Clique
    if clicada > -1:
        carta_clicada = deck_data[clicada]['nome_pt']
        
        if carta_clicada not in st.session_state['mao_selecionada']:
            if len(st.session_state['mao_selecionada']) < 6:
                st.session_state['mao_selecionada'].append(carta_clicada)
                st.toast(f"➕ Adicionada: {carta_clicada}")
            else:
                st.toast("⚠️ Mão cheia (Máx 6)!", icon="✋")
        else:
            st.session_state['mao_selecionada'].remove(carta_clicada)
            st.toast(f"➖ Removida: {carta_clicada}")
        
        # Reseta o ID para limpar a seleção visual da biblioteca (evita bugs)
        st.session_state['galeria_id'] += 1
        st.rerun()

else:
    st.error("Banco de dados vazio. Rode 'python gerar_banco_ia.py'")