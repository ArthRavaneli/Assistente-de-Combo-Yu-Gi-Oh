import streamlit as st
import json
import google.generativeai as genai
import os
import unicodedata
from st_clickable_images import clickable_images

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Yu-Gi-Oh! AI", page_icon="🐉", layout="wide")

# --- DEFINIÇÃO DA PASTA DE DECKS ---
PASTA_DECKS = "yu_gi_oh_decks"
if not os.path.exists(PASTA_DECKS):
    os.makedirs(PASTA_DECKS)

# --- CSS AVANÇADO (COM SUPORTE A IMAGENS NO TEXTO) ---
st.markdown("""
    <style>
        .block-container {padding-top: 3rem; padding-bottom: 5rem;}
        iframe {margin: auto; display: block;}
        
        div[data-testid="column"] > div > div > div > div > button {
            margin-top: -12px !important; padding-top: 0px !important;
            height: 25px; font-size: 10px;
        }

        /* --- ESTILOS DOS CARDS --- */
        .final-field {
            background-color: #2e2300; border-left: 6px solid #ffd700; 
            padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 16px;
        }

        /* Card do Passo (Agora com Flexbox para alinhar Imagem + Texto) */
        .combo-step {
            display: flex;              /* Alinha imagem e texto lado a lado */
            align-items: center;        /* Centraliza verticalmente */
            background-color: #131720; 
            border: 1px solid #2d3748; 
            border-left: 6px solid #00d4ff; 
            padding: 10px; 
            margin-bottom: 8px; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            transition: transform 0.2s;
        }
        .combo-step:hover {
            transform: translateX(5px);
            border-left-color: #00ff9d;
        }
        
        /* Estilo da Miniatura da Carta no Texto */
        .step-img {
            width: 45px;       /* Tamanho da miniatura */
            height: 65px;
            border-radius: 4px;
            margin-right: 15px; /* Espaço entre imagem e texto */
            border: 1px solid #555;
            flex-shrink: 0;    /* Garante que a imagem não amasse */
            object-fit: cover;
        }

        .step-content { width: 100%; }
        .step-action { color: #ffffff; font-weight: bold; font-size: 1.1em; line-height: 1.2;}
        .step-reason { color: #a0aec0; font-size: 0.9em; font-style: italic; display: block; margin-top: 4px;}
        
        .arrow-down { text-align: center; color: #555; font-size: 20px; margin: -5px 0 5px 0;}
        .risk-box {background-color: #2c0b0e; border-left: 6px solid #ff4b4b; padding: 15px; border-radius: 8px; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES BÁSICAS ---
def carregar_chave_arquivo():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return None

def listar_decks():
    # Lista arquivos da pasta yu_gi_oh_decks
    if not os.path.exists(PASTA_DECKS): return []
    arquivos = [f for f in os.listdir(PASTA_DECKS) if f.endswith('.json')]
    return [f for f in arquivos if not f.startswith('~')]

@st.cache_data
def carregar_banco_por_nome(nome_arquivo):
    caminho_completo = os.path.join(PASTA_DECKS, nome_arquivo)
    try:
        with open(caminho_completo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            dados.sort(key=lambda x: x['nome_pt'])
            return dados
    except Exception as e: 
        raise Exception(f"Erro ao carregar: {e}")

# --- FUNÇÃO NOVA: ENCONTRAR IMAGEM NO TEXTO ---
def normalizar_texto(texto):
    """Remove acentos e deixa minúsculo para facilitar a comparação."""
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def encontrar_imagem_carta(texto_passo, deck_data):
    """
    Varre o texto da IA e tenta achar o nome de alguma carta do deck dentro dele.
    Retorna a URL da imagem se encontrar.
    """
    texto_limpo = normalizar_texto(texto_passo)
    
    # Ordena por tamanho do nome (decrescente) para evitar falsos positivos em nomes curtos
    deck_ordenado = sorted(deck_data, key=lambda x: len(x['nome_pt']), reverse=True)
    
    for carta in deck_ordenado:
        nome_pt = normalizar_texto(carta.get('nome_pt', ''))
        nome_en = normalizar_texto(carta.get('nome_ingles', ''))
        
        # Verifica se o nome (PT ou EN) está contido na frase limpa
        if (nome_pt and nome_pt in texto_limpo) or (nome_en and nome_en in texto_limpo):
            return carta['imagem']
            
    return None

# --- RENDERIZAÇÃO DA GALERIA ---
def renderizar_galeria(titulo, lista_cartas, key_suffix, colunas_fixas=None):
    if not lista_cartas: return
    st.markdown(f"### {titulo}")
    
    zoom_nivel = st.session_state.get('zoom_nivel_slider', 130)
    imagens = [c["imagem"] for c in lista_cartas]
    titulos = [f"{c['nome_pt']} (x{c.get('qtd_maxima', 1)})" for c in lista_cartas]

    clique = clickable_images(
        imagens, titles=titulos,
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap", "background-color": "#0e1117", "padding": "10px"},
        img_style={"margin": "4px", "height": f"{zoom_nivel}px", "cursor": "pointer", "border-radius": "4px"},
        key=f"galeria_{key_suffix}_{st.session_state['galeria_id']}"
    )
    
    if clique > -1:
        carta = lista_cartas[clique]
        nome = carta['nome_pt']
        limit = carta.get('qtd_maxima', 1)
        atual = st.session_state['mao_real'].count(nome)
        
        if atual < limit:
            st.session_state['mao_real'].append(nome)
            st.toast(f"➕ {nome}")
        else:
            st.toast(f"⚠️ Máximo {limit}!", icon="🛑")
        
        st.session_state['galeria_id'] += 1
        st.rerun()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel")
    st.session_state['zoom_nivel_slider'] = st.slider("🔍 Zoom", 80, 250, 130, 10)
    
    if carregar_chave_arquivo(): api_key = carregar_chave_arquivo()
    else: api_key = st.text_input("API Key:", type="password")
    
    decks_encontrados = listar_decks()
    if decks_encontrados:
        deck_selecionado_nome = st.selectbox("📚 Escolha o Deck:", decks_encontrados)
    else:
        deck_selecionado_nome = None
        st.warning(f"Nenhum deck na pasta '{PASTA_DECKS}'.")
        
    if deck_selecionado_nome:
        default_name = deck_selecionado_nome.replace(".json", "").replace("_", " ").title()
    else: default_name = "Carregando..."
    archetype = st.text_input("Nome do Deck:", value=default_name)
    
    if 'mao_real' not in st.session_state: st.session_state['mao_real'] = []
    if 'galeria_id' not in st.session_state: st.session_state['galeria_id'] = 0

    st.divider()
    st.write(f"**Mão:** {len(st.session_state['mao_real'])}")
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state['mao_real'] = []
        st.rerun()

# --- CARREGAMENTO ---
if deck_selecionado_nome:
    try: deck_data = carregar_banco_por_nome(deck_selecionado_nome)
    except Exception as e: st.error(f"Erro: {e}"); deck_data = []
else: deck_data = []

# --- INTERFACE PRINCIPAL ---
st.title(f"🐉 Galeria de Duelo ({deck_selecionado_nome.replace('.json', '') if deck_selecionado_nome else 'Nenhum'})")

if deck_data:
    st.markdown("#### ✋ Sua Mão Atual:")
    if st.session_state['mao_real']:
        cols = st.columns(10)
        w_calc = int(st.session_state['zoom_nivel_slider'] * 0.71)
        for i, nome in enumerate(st.session_state['mao_real']):
            if i < 10:
                d = next((c for c in deck_data if c['nome_pt'] == nome), None)
                if d:
                    with cols[i]:
                        st.image(d['imagem'], width=w_calc)
                        if st.button("❌", key=f"del_{i}"):
                            st.session_state['mao_real'].pop(i)
                            st.rerun()
    else: st.info("Clique nas cartas abaixo.")

    st.divider()

    # --- ANÁLISE ---
    if st.session_state['mao_real']:
        if st.button("🧠 ANALISAR JOGADA (COM IMAGENS)", type="primary", use_container_width=True):
            if not api_key: st.error("Faltou API Key")
            else:
                with st.spinner("Processando..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        objs = [d for n in st.session_state['mao_real'] for d in deck_data if d['nome_pt'] == n]
                        detalhes = "\n".join([f"- {c['nome_pt']}: {c['efeito']}" for c in objs])
                        
                        prompt = f"""
                        ATUE COMO: Pro Player de Yu-Gi-Oh.
                        DECK: {archetype}. MÃO: {', '.join([c['nome_pt'] for c in objs])}
                        DETALHES: {detalhes}
                        OBJETIVO: Melhor combo Turno 1.
                        REGRAS DE RESPOSTA:
                        1. USE EXATAMENTE O NOME DA CARTA EM PORTUGUÊS (Como está nos detalhes).
                        2. Responda APENAS neste formato:
                        CAMPO_FINAL: (Resumo)
                        RISCOS: (Resumo)
                        COMBO_START
                        Ação 1 (Motivo) ||| Ação 2 (Motivo) ||| ...
                        COMBO_END
                        """
                        raw_res = model.generate_content([prompt], generation_config={"temperature": 0.4}).text
                        st.session_state['analise_raw'] = raw_res
                    except Exception as e: st.error(f"Erro IA: {e}")

    # --- RENDERIZAÇÃO VISUAL COM IMAGENS ---
    if 'analise_raw' in st.session_state:
        texto = st.session_state['analise_raw']
        try:
            campo_final = ""; riscos = ""; passos_combo = []; lines = texto.split('\n'); modo = False
            for l in lines:
                if "CAMPO_FINAL:" in l: campo_final = l.replace("CAMPO_FINAL:", "").strip()
                elif "RISCOS:" in l: riscos = l.replace("RISCOS:", "").strip()
                elif "COMBO_START" in l: modo = True
                elif "COMBO_END" in l: modo = False
                elif modo: 
                    for p in l.split("|||"): 
                        if p.strip(): passos_combo.append(p.strip())

            if campo_final: 
                html_final = f'<div class="final-field">🎯 <b>CAMPO FINAL:</b> {campo_final.replace("**", "")}</div>'
                st.markdown(html_final, unsafe_allow_html=True)
            
            st.markdown("### ⚡ Sequência:")
            
            for i, passo in enumerate(passos_combo):
                acao = passo.split("(")[0].strip().replace("**", "")
                motivo = passo.split("(")[1].replace(")", "").strip().replace("**", "") if "(" in passo else ""
                
                # --- BUSCA IMAGEM ---
                img_url = encontrar_imagem_carta(acao, deck_data)
                img_html = f'<img src="{img_url}" class="step-img">' if img_url else ''
                
                # --- HTML SEM INDENTAÇÃO (CORRIGIDO) ---
                html_card = f"""
<div class="combo-step">
{img_html}
<div class="step-content">
<div class="step-action">{acao}</div>
{f'<span class="step-reason">💡 {motivo}</span>' if motivo else ''}
</div>
</div>
"""
                st.markdown(html_card, unsafe_allow_html=True)
                
                if i < len(passos_combo) - 1: 
                    st.markdown('<div class="arrow-down">⬇</div>', unsafe_allow_html=True)

            if riscos: 
                html_risco = f'<div class="risk-box">⚠️ <b>ATENÇÃO / RISCOS:</b><br>{riscos.replace("**", "")}</div>'
                st.markdown(html_risco, unsafe_allow_html=True)
        except: 
            st.warning("Visualização simples (IA fugiu do formato):")
            st.write(texto)

    st.markdown("---")
    main = [c for c in deck_data if not any(x in c['tipo'].lower() for x in ["fusion", "synchro", "xyz", "link"])]
    extra = [c for c in deck_data if any(x in c['tipo'].lower() for x in ["fusion", "synchro", "xyz", "link"])]
    main.sort(key=lambda x: x['nome_pt']); extra.sort(key=lambda x: x['nome_pt'])
    renderizar_galeria("📖 Main Deck", main, "main", colunas_fixas=10)
    renderizar_galeria("🟣 Extra Deck", extra, "extra", colunas_fixas=6)
else:
    st.error(f"Nenhum deck encontrado na pasta '{PASTA_DECKS}'.")