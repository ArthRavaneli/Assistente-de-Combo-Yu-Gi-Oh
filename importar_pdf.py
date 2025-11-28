import google.generativeai as genai
import requests
import json
import time
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÃO DE CAMINHOS ---
PASTA_DECKS = "yu_gi_oh_decks"

if not os.path.exists(PASTA_DECKS):
    os.makedirs(PASTA_DECKS)

def pegar_chave():
    try:
        with open("api_key.txt", "r") as f: return f.read().strip()
    except: return None

API_KEY = pegar_chave()

# --- FUNÇÕES DE API E DESIGN ---
def buscar_dados_api(nome_ingles):
    url_api = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    # Tenta pegar dados técnicos
    try:
        r = requests.get(url_api, params={"name": nome_ingles})
        data = r.json()
        if "data" in data: return data["data"][0]
    except: pass
    return None

def processar_imagem_com_badge(url_imagem, quantidade):
    try:
        response = requests.get(url_imagem)
        img = Image.open(BytesIO(response.content))
        if quantidade > 1:
            draw = ImageDraw.Draw(img)
            largura, altura = img.size
            texto = f"x{quantidade}"
            try: font = ImageFont.truetype("arial.ttf", 50)
            except: font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), texto, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x1, y0 = largura - 20, int(altura * 0.40)
            x0, y1 = x1 - w - 20, y0 + h + 16
            draw.rectangle([x0, y0, x1, y1], fill="#D32F2F", outline="white", width=3)
            draw.text((x0 + 10, y0 + 4), texto, fill="white", font=font, stroke_width=2, stroke_fill="black")
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    except: return url_imagem

# --- FUNÇÃO PRINCIPAL ---
def criar_deck_via_pdf():
    print("\n--- 📑 IMPORTADOR DECK PDF COM IA (PT-BR) ---")
    print(f"📂 Buscando PDFs em: ./{PASTA_DECKS}/\n")
    
    arquivos = [f for f in os.listdir(PASTA_DECKS) if f.lower().endswith('.pdf')]
    
    if not arquivos:
        print(f"❌ Nenhum PDF encontrado na pasta '{PASTA_DECKS}'.")
        return

    print("Decks encontrados:")
    for i, arquivo in enumerate(arquivos):
        print(f" [{i+1}] {arquivo}")
    
    print("")
    escolha = input("Digite o NÚMERO do arquivo: ").strip()

    try:
        indice = int(escolha) - 1
        if 0 <= indice < len(arquivos):
            pdf_selecionado = arquivos[indice]
        else:
            print("❌ Número inválido."); return
    except ValueError:
        print("❌ Digite um número."); return

    pdf_arquivo_full = os.path.join(PASTA_DECKS, pdf_selecionado)
    base_name = os.path.splitext(pdf_selecionado)[0]
    caminho_json_saida = os.path.join(PASTA_DECKS, f"{base_name}.json")

    print(f"\n✅ Selecionado: {pdf_selecionado}")
    
    if not API_KEY: print("❌ Sem API Key."); return

    print(f"👁️ Enviando para tradução e análise (Gemini Flash)...")
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    try:
        pdf_file = genai.upload_file(pdf_arquivo_full) 
    except Exception as e:
        print(f"❌ Erro upload: {e}"); return

    # --- PROMPT QUE FORÇA O PORTUGUÊS ---
    prompt = f"""
    Analise o PDF anexo (deck Yu-Gi-Oh).
    Extraia as cartas do 'Main Deck' e 'Extra Deck'. IGNORE Side Deck.
    
    Para CADA carta, retorne:
    1. "en": Nome exato em INGLÊS (como no PDF).
    2. "pt": A tradução oficial ou comum em PORTUGUÊS (PT-BR).
    3. "qtd": Quantidade.

    Responda EXCLUSIVAMENTE JSON:
    {{ 
        "cartas": [ 
            {{"en": "Blue-Eyes White Dragon", "pt": "Dragão Branco de Olhos Azuis", "qtd": 3}}, 
            ... 
        ] 
    }}
    """
    
    lista_cartas = []
    try:
        response = model.generate_content([prompt, pdf_file], generation_config={"response_mime_type": "application/json"})
        dados_ia = json.loads(response.text)
        lista_cartas = dados_ia.get("cartas", [])
    except Exception as e:
        print(f"❌ Erro análise: {e}"); return
    finally:
        try: genai.delete_file(pdf_file.name)
        except: pass
    
    if not lista_cartas: print("❌ Nenhuma carta extraída."); return
        
    print(f"\n📊 Processando {len(lista_cartas)} cartas (Aplicando tradução)...")
    print("-" * 50)
    
    banco_final = []
    for item in lista_cartas:
        name_en = item.get("en")
        name_pt = item.get("pt") # Pega a tradução da IA
        qtd = item.get("qtd", 1)
        
        # Busca imagem usando nome em Inglês (mais seguro)
        dados_api = buscar_dados_api(name_en)
        
        if dados_api:
            print(f"✅ {name_pt} (x{qtd})") # Mostra o nome em PT no console
            img = processar_imagem_com_badge(dados_api["card_images"][0]["image_url_small"], qtd)
            
            banco_final.append({
                "nome_pt": name_pt,      # Salva o nome traduzido pela IA
                "nome_ingles": name_en,  # Salva o inglês para referência
                "tipo": dados_api["type"],
                "efeito": dados_api["desc"],
                "imagem": img,
                "qtd_maxima": qtd
            })
        else:
            print(f"⚠️ API não achou imagem: {name_en}")
        time.sleep(0.05)

    with open(caminho_json_saida, "w", encoding="utf-8") as f:
        json.dump(banco_final, f, indent=4, ensure_ascii=False)
    
    print("-" * 50)
    print(f"🎉 SUCESSO! Deck salvo em: {caminho_json_saida}")
    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    criar_deck_via_pdf()