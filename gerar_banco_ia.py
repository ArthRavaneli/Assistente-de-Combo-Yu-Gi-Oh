import google.generativeai as genai
import requests
import json
import time
import os

# --- FUNÇÃO PARA LER A CHAVE ---
def pegar_chave():
    try:
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Erro: Crie o arquivo 'api_key.txt' com sua chave dentro!")
        return None

API_KEY = pegar_chave()

# --- SUA LISTA (BLUE-EYES) ---
minha_lista_pt = [
    "Dragão Branco de Olhos Azuis",
    "A Pedra Branca das Lendas",
    "Sábio com Azul nos Olhos",
    "A Pedra Branca dos Antigos",
    "Florescer de Cinzas & Primavera Feliz",
    "Ditador dos Dragões",
    "Dragão Branco Alternativo de Olhos Azuis",
    "Espírito Dragão de Branco",
    "Dragão do Abismo de Olhos Azuis",
    "Dragão Jato de Olhos Azuis",
    "Dragão Branco de Olhos Profundos",
    "Dragão MÁX do Caos de Olhos Azuis",
    "Raigeki",
    "Reviver Monstro",
    "Trocar",
    "Tempestade de Relâmpagos",
    "A Melodia do Despertar do Dragão",
    "Cards da Consonância",
    "Retorno dos Senhores Dragão",
    "Forma do Caos",
    "Alma do Sucessor",
    "Fusão Definitiva",
    "Impermanência Infinita",
    "A Criatura Definitiva da Destruição",
    "Rivais Destinados",
    "Luz Verdadeira",
    "Dragão Tirano de Olhos Azuis",
    "Dragão Gêmeo da Explosão de Olhos Azuis",
    "Dragão Prateado de Olhos Cerúleos",
    "Dragão Espírito de Olhos Azuis",
    "Dragão Solar Hierático Suserano de Heliópolis",
    "Dragão-Guarda Pisty",
    'Maxx "C"',
    "Nibiru, o Ser Primitivo",
    "Chamado pela Cova",
    "Designador de Cancelamento"
]

# --- CORREÇÕES MANUAIS (RECOLOCADAS AQUI) ---
CORRECOES_MANUAIS = {
    "Dragão Gêmeo da Explosão de Olhos Azuis": "Blue-Eyes Twin Burst Dragon",
    "Dragão Solar Hierático Suserano de Heliópolis": "Hieratic Sun Dragon Overlord of Heliopolis",
    "Dragão MÁX do Caos de Olhos Azuis": "Blue-Eyes Chaos MAX Dragon",
    "Dragão Tirano de Olhos Azuis": "Blue-Eyes Tyrant Dragon",
    "Sábio com Azul nos Olhos": "Sage with Eyes of Blue",
    "Dragão Jato de Olhos Azuis": "Blue-Eyes Jet Dragon",
    "Dragão Branco de Olhos Profundos": "Deep-Eyes White Dragon"
}

def traduzir_nomes(lista_pt):
    print("🤖 A IA está traduzindo os nomes...")
    if not API_KEY: return {}

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Traduza esta lista de cartas de Yu-Gi-Oh (Master Duel PT-BR) para INGLÊS OFICIAL (TCG).
    LISTA: {lista_pt}
    Responda apenas JSON: {{"Nome PT": "Nome EN"}}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Erro na tradução: {e}")
        return {}

def criar_banco_inteligente():
    mapa_traducao = traduzir_nomes(minha_lista_pt)
    
    if not mapa_traducao: return

    if CORRECOES_MANUAIS:
        print("🔧 Aplicando correções manuais de Blue-Eyes...")
        mapa_traducao.update(CORRECOES_MANUAIS)

    print("-" * 50)
    print("🌍 Baixando dados e IMAGENS da API...")
    
    banco_final = []
    
    for nome_pt, nome_ingles in mapa_traducao.items():
        url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        try:
            r = requests.get(url, params={"name": nome_ingles})
            data = r.json()
            
            if "data" in data:
                carta_api = data["data"][0]
                print(f"✅ {nome_pt}")
                
                banco_final.append({
                    "nome_pt": nome_pt,
                    "nome_ingles": nome_ingles,
                    "tipo": carta_api["type"],
                    "efeito": carta_api["desc"],
                    # SALVANDO A IMAGEM COMPLETA (small)
                    "imagem": carta_api["card_images"][0]["image_url_small"]
                })
            else:
                print(f"⚠️ API não achou: '{nome_ingles}'")
                
        except: pass
        time.sleep(0.05)

    with open("master_duel_deck.json", "w", encoding="utf-8") as f:
        json.dump(banco_final, f, indent=4, ensure_ascii=False)
    
    print("-" * 50)
    print(f"🎉 Banco Atualizado! {len(banco_final)} cartas prontas.")

if __name__ == "__main__":
    criar_banco_inteligente()