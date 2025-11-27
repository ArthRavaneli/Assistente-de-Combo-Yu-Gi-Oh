import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# --- PALETA DE CORES (TEMA FARAÓ / OLHO DE HÓRUS) ---
COR_FUNDO = "#0A0A0A"       # Preto profundo
COR_TEXTO_OURO = "#E5C15D"  # Dourado metálico (títulos)
COR_TEXTO_CLARO = "#F0E6D2" # Bege claro (textos menores)
COR_BTN_PRINCIPAL = "#D4AF37" # Ouro vibrante (botão iniciar)
COR_BTN_PRINCIPAL_HOVER = "#F7E7A8" # Ouro mais claro (ao passar o mouse)
COR_BTN_SECUNDARIO = "#8B0000" # Vermelho sangue escuro (botão importar)
COR_BTN_SECUNDARIO_HOVER = "#A52A2A" # Vermelho mais claro
COR_STATUS_VERMELHO = "#C0392B" # Vermelho alerta
COR_STATUS_DOURADO = "#B7950B" # Dourado escuro (sucesso)

class YuGiOhLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Yu-Gi-Oh! AI - Domínio do Faraó")
        self.root.geometry("500x420")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(False, False)

        # --- ÍCONE (Opcional) ---
        # if os.path.exists("icone.ico"): self.root.iconbitmap("icone.ico")

        # --- ESTILOS (CSS DO TKINTER - TEMA EGÍPCIO) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Estilo do Botão Principal (OURO)
        self.style.configure("Gold.TButton", 
            font=('Cinzel Decorative', 12, 'bold'), # Fonte estilo antigo (se não tiver, usa padrão)
            background=COR_BTN_PRINCIPAL,
            foreground="#2C2C2C", # Texto escuro para contraste no ouro
            borderwidth=2,
            relief="raised",
            padding=15
        )
        self.style.map("Gold.TButton", 
            background=[('active', COR_BTN_PRINCIPAL_HOVER), ('disabled', '#4A4A4A')],
            foreground=[('disabled', '#808080')]
        )

        # Estilo do Botão Secundário (VERMELHO)
        self.style.configure("Red.TButton", 
            font=('Cinzel Decorative', 11),
            background=COR_BTN_SECUNDARIO,
            foreground=COR_TEXTO_CLARO,
            borderwidth=2,
            relief="raised",
            padding=15
        )
        self.style.map("Red.TButton", 
            background=[('active', COR_BTN_SECUNDARIO_HOVER), ('disabled', '#4A4A4A')],
            foreground=[('disabled', '#808080')]
        )

        # --- INTERFACE ---
        self.criar_widgets()

    def criar_widgets(self):
        # 1. Cabeçalho Dourado
        header_frame = tk.Frame(self.root, bg=COR_FUNDO, height=100)
        header_frame.pack(fill="x", pady=(20, 0))
        
        # Título com "brilho"
        title_lbl = tk.Label(header_frame, text="𓂀 DUEL ASSISTANT AI 𓂀", 
                             font=("Segoe UI Historic", 24, "bold"), 
                             bg=COR_FUNDO, fg=COR_TEXTO_OURO)
        title_lbl.pack(pady=10)
        
        subtitle_lbl = tk.Label(header_frame, text="A Sabedoria do Milênio ao seu Alcance", 
                                font=("Segoe UI Historic", 10), 
                                bg=COR_FUNDO, fg=COR_TEXTO_CLARO)
        subtitle_lbl.pack()

        # 2. Área de Conteúdo
        content_frame = tk.Frame(self.root, bg=COR_FUNDO)
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)

        # Botão App (Destaque Dourado)
        self.btn_app = ttk.Button(content_frame, text="⚡ INICIAR APLICATIVO", 
                                  style="Gold.TButton",
                                  cursor="hand2",
                                  command=lambda: self.executar_seguro(self.abrir_app, self.btn_app))
        self.btn_app.pack(fill="x", pady=(0, 15))

        # Botão Importar (Secundário Vermelho)
        self.btn_import = ttk.Button(content_frame, text="📜 IMPORTAR PERGAMINHO (PDF)", 
                                     style="Red.TButton",
                                     cursor="hand2",
                                     command=lambda: self.executar_seguro(self.abrir_importador, self.btn_import))
        self.btn_import.pack(fill="x", pady=0)

        # Descrição
        desc_lbl = tk.Label(content_frame, 
                            text="v2.0 • Sistema RAG • Visão de Hórus", 
                            font=("Segoe UI Historic", 8), bg=COR_FUNDO, fg="#666666")
        desc_lbl.pack(side="bottom", pady=10)

        # 3. Barra de Status
        self.status_bar = tk.Label(self.root, text="Aguardando comando do Faraó...", 
                                   font=("Consolas", 9), bg="#222222", fg=COR_TEXTO_OURO, anchor="w", padx=10, pady=5)
        self.status_bar.pack(side="bottom", fill="x")

    # --- LÓGICA DE SISTEMA (Igual ao anterior) ---
    def verificar_arquivos(self):
        arquivos = ["venv", "app.py", "importar_pdf.py"]
        missing = [f for f in arquivos if not os.path.exists(f)]
        if missing:
            messagebox.showerror("Erro", f"Arquivos sagrados faltando:\n{', '.join(missing)}")
            return False
        return True

    def executar_seguro(self, funcao_comando, botao):
        if not self.verificar_arquivos(): return
        botao.config(state="disabled")
        self.status_bar.config(text="⏳ Invocando poder... aguarde...", bg=COR_BTN_SECUNDARIO, fg=COR_TEXTO_CLARO)
        self.root.update()
        funcao_comando()
        self.root.after(3000, lambda: self.resetar_botao(botao))

    def resetar_botao(self, botao):
        botao.config(state="normal")
        self.status_bar.config(text="✅ Comando executado. O destino foi selado.", bg=COR_STATUS_DOURADO, fg="#222222")

    def rodar_cmd(self, comando, titulo):
        caminho_python = os.path.join("venv", "Scripts", "python.exe")
        full_cmd = f'start "{titulo}" cmd /k "{caminho_python} {comando}"'
        os.system(full_cmd)

    def abrir_app(self):
        self.rodar_cmd("-m streamlit run app.py", "Yu-Gi-Oh! AI - Servidor")

    def abrir_importador(self):
        self.rodar_cmd("importar_pdf.py", "Importador de Decks")

if __name__ == "__main__":
    root = tk.Tk()
    app = YuGiOhLauncher(root)
    root.mainloop()