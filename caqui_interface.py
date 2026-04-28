import os
import sys
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox
import pythoncom
from gerar_termo import GeradorDeTermos
from usuario_service import (
    obter_usuario_sistema,
    obter_nome_pasta_drive,
    localizar_pasta_drive_usuario,
    mover_para_pasta_drive,
)

# ============================================================
# 💡 FUNÇÃO CRÍTICA PARA CORRIGIR CAMINHOS DO PYINSTALLER
# ============================================================

def recurso_executavel(relative_path):
    """Obtém o caminho absoluto para o recurso, seja no modo de desenvolvimento
    ou no modo de executável PyInstaller.
    """
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(os.path.abspath("."))
    return base_path / relative_path


# ============================================================
# ⚙️ CONFIGURAÇÕES
# ============================================================

PASTA_LOCAL = Path.cwd()

# ============================================================
# 🎨 TEMA "CAQUI" v2 — REDESIGN MODERNO
# ============================================================

# Backgrounds — camadas de profundidade
COLOR_BG           = "#1A1816"
COLOR_SURFACE      = "#242220"
COLOR_SURFACE_ALT  = "#2E2B28"

# Sidebar
COLOR_SIDEBAR      = "#1E1C1A"
COLOR_SIDEBAR_SEL  = "#2E2A26"

# Accent — laranja vibrante
COLOR_PRIMARY      = "#E08A00"
COLOR_PRIMARY_DARK = "#B86E00"
COLOR_PRIMARY_GLOW = "#E08A0025"

# Texto — hierarquia
COLOR_TEXT         = "#F5EDE0"
COLOR_TEXT_DIM     = "#9E9388"
COLOR_TEXT_MUTED   = "#6B6560"

# Feedback
COLOR_SUCCESS      = "#4CAF50"
COLOR_ERROR        = "#E74C3C"
COLOR_BORDER       = "#3A3633"

# Layout
PADDING_X       = 30
SPACING_FIELD_Y = 14
HEIGHT_ENTRY    = 42
SIDEBAR_WIDTH   = 180


# ============================================================
# 🧠 FUNÇÕES AUXILIARES
# ============================================================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ============================================================
# 🖥️ INTERFACE GRÁFICA — REDESIGN v2
# ============================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ==============================
        # JANELA PRINCIPAL
        # ==============================
        self.title("Caquímetro - Gerador de Termos")
        self.geometry("920x780")
        self.minsize(850, 700)

        # Ícone
        try:
            self.iconbitmap(resource_path("caqui.ico"))
        except Exception:
            pass

        # Tema escuro fixo
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BG)

        # Layout raiz: sidebar (col 0) + conteúdo (col 1)
        self.grid_columnconfigure(0, weight=0, minsize=SIDEBAR_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Dados do usuário
        self.usuario = obter_usuario_sistema()
        self.nome_drive = obter_nome_pasta_drive()
        self.tipo_selecionado = "Equipamento"
        self.campos = {}
        self.progress_bar = None
        self._toast_after_id = None

        # ==============================
        # SIDEBAR
        # ==============================
        self._criar_sidebar()

        # ==============================
        # ÁREA PRINCIPAL
        # ==============================
        self._criar_area_principal()

        # ==============================
        # BARRA DE STATUS
        # ==============================
        self._criar_barra_status()

    # ============================================================
    # 🏗️ CONSTRUÇÃO DA SIDEBAR
    # ============================================================
    def _criar_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            fg_color=COLOR_SIDEBAR,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Logo / título da sidebar
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=15, pady=(25, 30), sticky="ew")

        ctk.CTkLabel(
            logo_frame,
            text="🍊",
            font=("Segoe UI", 32),
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            logo_frame,
            text="Caquímetro",
            font=("Segoe UI", 16, "bold"),
            text_color=COLOR_PRIMARY
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="Gerador de Termos",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_DIM
        ).pack()

        # Separador
        ctk.CTkFrame(
            self.sidebar, height=1,
            fg_color=COLOR_BORDER
        ).grid(row=1, column=0, padx=20, sticky="ew")

        # Label de seção
        ctk.CTkLabel(
            self.sidebar,
            text="TIPO DE TERMO",
            font=("Segoe UI", 9, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        ).grid(row=2, column=0, padx=20, pady=(20, 8), sticky="w")

        # Botões de navegação (icon + texto em grid para alinhamento)
        self.nav_buttons = {}
        nav_items = [
            ("Equipamento",         "💻", "Equipamento"),   
            ("VPN",                 "🛡️", "VPN"),           
            ("Administrador Local", "🧑‍💻", "Admin Local"),     
            ("Telecom",             "📞", "Telecom"),         
        ]

        for i, (key, icon, label) in enumerate(nav_items):
            # Frame clicável como botão
            nav_frame = ctk.CTkFrame(
                self.sidebar,
                height=42,
                corner_radius=10,
                fg_color="transparent",
                cursor="hand2"
            )
            nav_frame.grid(row=3 + i, column=0, padx=10, pady=2, sticky="ew")
            nav_frame.grid_propagate(False)
            nav_frame.grid_columnconfigure(0, minsize=28)
            nav_frame.grid_columnconfigure(1, weight=1)
            nav_frame.grid_rowconfigure(0, weight=1)

            icon_lbl = ctk.CTkLabel(
                nav_frame,
                text=icon,
                font=("Segoe UI", 14),
                width=28,
                anchor="center",
                text_color=COLOR_TEXT_DIM
            )
            icon_lbl.grid(row=0, column=0, padx=(10, 0))

            text_lbl = ctk.CTkLabel(
                nav_frame,
                text=label,
                font=("Segoe UI", 13),
                text_color=COLOR_TEXT_DIM,
                anchor="w"
            )
            text_lbl.grid(row=0, column=1, padx=(4, 8), sticky="w")

            # Tornar todo o frame clicável
            cmd = lambda k=key: self._selecionar_tipo(k)
            nav_frame.bind("<Button-1>", lambda e, c=cmd: c())
            icon_lbl.bind("<Button-1>", lambda e, c=cmd: c())
            text_lbl.bind("<Button-1>", lambda e, c=cmd: c())

            # Hover effect no frame
            nav_frame.bind("<Enter>", lambda e, f=nav_frame: f.configure(
                fg_color=COLOR_SURFACE_ALT) if f != self._get_active_nav() else None)
            nav_frame.bind("<Leave>", lambda e, f=nav_frame: f.configure(
                fg_color="transparent") if f != self._get_active_nav() else None)

            self.nav_buttons[key] = (nav_frame, icon_lbl, text_lbl)

        # Selecionar o primeiro por padrão
        self._destacar_nav("Equipamento")

        # Espaçador para empurrar status para baixo
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Status do drive na sidebar
        drive_status = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        drive_status.grid(row=11, column=0, padx=15, pady=(0, 20), sticky="sew")

        ctk.CTkLabel(
            drive_status,
            text="● Drive",
            font=("Segoe UI", 11),
            text_color=COLOR_SUCCESS,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            drive_status,
            text=f"Pasta: {self.nome_drive}",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w")

    def _get_active_nav(self):
        """Retorna o frame do nav ativo para evitar remover hover do selecionado."""
        data = self.nav_buttons.get(self.tipo_selecionado)
        return data[0] if data else None

    def _selecionar_tipo(self, tipo):
        self.tipo_selecionado = tipo
        self._destacar_nav(tipo)
        self.atualizar_campos(tipo)

    def _destacar_nav(self, tipo_ativo):
        for key, (frame, icon_lbl, text_lbl) in self.nav_buttons.items():
            if key == tipo_ativo:
                frame.configure(fg_color=COLOR_SIDEBAR_SEL)
                text_lbl.configure(text_color=COLOR_PRIMARY)
            else:
                frame.configure(fg_color="transparent")
                text_lbl.configure(text_color=COLOR_TEXT_DIM)

    # ============================================================
    # 🏗️ ÁREA PRINCIPAL (conteúdo)
    # ============================================================
    def _criar_area_principal(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)
        self.main_frame = main

        # ── Card de Usuário (glassmorphism) ──
        user_card = ctk.CTkFrame(
            main,
            fg_color=COLOR_SURFACE,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER
        )
        user_card.grid(row=0, column=0, padx=PADDING_X, pady=(20, 10), sticky="ew")
        user_card.grid_columnconfigure(1, weight=1)

        # Avatar circular
        avatar = ctk.CTkLabel(
            user_card,
            text=self.usuario[0].upper() if self.usuario else "?",
            font=("Segoe UI", 18, "bold"),
            fg_color=COLOR_PRIMARY,
            corner_radius=22,
            width=44,
            height=44,
            text_color="white"
        )
        avatar.grid(row=0, column=0, rowspan=2, padx=(18, 14), pady=16)

        ctk.CTkLabel(
            user_card,
            text=self.usuario.upper(),
            font=("Segoe UI", 15, "bold"),
            text_color=COLOR_TEXT,
            anchor="w"
        ).grid(row=0, column=1, sticky="sw", pady=(16, 0))

        ctk.CTkLabel(
            user_card,
            text=f"📂  Google Drive  ›  {self.nome_drive}",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_DIM,
            anchor="w"
        ).grid(row=1, column=1, sticky="nw", pady=(2, 16))

        # ── Título da seção de formulário ──
        self.section_title_label = ctk.CTkLabel(
            main,
            text="",
            font=("Segoe UI", 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.section_title_label.grid(row=1, column=0, padx=PADDING_X + 5, pady=(10, 0), sticky="w")

        # ── Área rolável de campos ──
        self.frame_scroll = ctk.CTkScrollableFrame(
            main,
            fg_color="transparent",
            scrollbar_button_color=COLOR_SURFACE_ALT,
            scrollbar_button_hover_color=COLOR_PRIMARY_DARK
        )
        self.frame_scroll.grid(row=2, column=0, padx=PADDING_X, pady=(5, 10), sticky="nsew")
        self.frame_scroll.grid_columnconfigure(0, weight=1)

        self.frame_campos = ctk.CTkFrame(self.frame_scroll, fg_color="transparent")
        self.frame_campos.grid(row=0, column=0, sticky="new")
        self.frame_campos.columnconfigure(0, weight=1, uniform="col")
        self.frame_campos.columnconfigure(1, weight=1, uniform="col")

        self.atualizar_campos("Equipamento")

        # ── Botão principal ──
        btn_frame = ctk.CTkFrame(self.frame_scroll, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(25, 15), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        self.btn_submit = ctk.CTkButton(
            btn_frame,
            text="  🚀  GERAR E ENVIAR TERMO",
            command=self.executar_processo_thread,
            width=340,
            height=56,
            font=("Segoe UI", 15, "bold"),
            corner_radius=14,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="white"
        )
        self.btn_submit.grid(row=0, column=0)

        # ── Toast container (notificações inline) ──
        self.toast_frame = ctk.CTkFrame(
            main,
            fg_color="transparent",
            height=0
        )
        self.toast_frame.grid(row=3, column=0, padx=PADDING_X, sticky="ew")
        self.toast_frame.grid_propagate(False)

        self.toast_label = ctk.CTkLabel(
            self.toast_frame,
            text="",
            font=("Segoe UI", 12, "bold"),
            corner_radius=10,
            height=40,
            anchor="center"
        )
        self.toast_label.pack(fill="x", padx=0, pady=5)

    # ============================================================
    # 🏗️ BARRA DE STATUS
    # ============================================================
    def _criar_barra_status(self):
        status_bar = ctk.CTkFrame(
            self,
            height=32,
            fg_color=COLOR_SURFACE,
            corner_radius=0
        )
        status_bar.grid(row=1, column=1, sticky="sew")
        status_bar.grid_propagate(False)

        ctk.CTkLabel(
            status_bar,
            text=f"👤 {self.usuario}",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_DIM
        ).pack(side="left", padx=15, pady=4)

        ctk.CTkLabel(
            status_bar,
            text="v2.0",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="right", padx=15, pady=4)

        # Progress bar dentro da status bar
        self.progress_bar = ctk.CTkProgressBar(
            status_bar,
            width=200,
            height=6,
            progress_color=COLOR_PRIMARY,
            fg_color=COLOR_SURFACE_ALT,
            corner_radius=3
        )
        # Inicialmente escondida, será mostrada durante processamento

    # ============================================================
    # 🍞 TOAST — Notificações inline
    # ============================================================
    def _mostrar_toast(self, mensagem, tipo="info", duracao=4000):
        """Exibe uma notificação inline temporária.
        tipo: 'success', 'error', 'warning', 'info'
        """
        cores = {
            "success": (COLOR_SUCCESS, "#1B3A1B"),
            "error":   (COLOR_ERROR,   "#3A1B1B"),
            "warning": (COLOR_PRIMARY, "#3A2E1B"),
            "info":    (COLOR_TEXT_DIM, COLOR_SURFACE),
        }
        text_color, bg_color = cores.get(tipo, cores["info"])

        # Cancelar toast anterior se existir
        if self._toast_after_id:
            self.after_cancel(self._toast_after_id)

        self.toast_label.configure(
            text=mensagem,
            text_color=text_color,
            fg_color=bg_color
        )
        self.toast_frame.configure(height=50)

        self._toast_after_id = self.after(duracao, self._esconder_toast)

    def _esconder_toast(self):
        self.toast_frame.configure(height=0)
        self._toast_after_id = None

    # ============================================================
    # 📝 CRIAÇÃO DE CAMPOS (com placeholder e focus)
    # ============================================================
    def _criar_campo(self, parent, label_text, placeholder="", row=0, col=0, colspan=1):
        """Cria um campo de entrada estilizado com label, placeholder e focus state."""
        lbl = ctk.CTkLabel(
            parent,
            text=label_text,
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            text_color=COLOR_TEXT_DIM
        )
        lbl.grid(row=row, column=col, columnspan=colspan, sticky="w", padx=12, pady=(SPACING_FIELD_Y, 0))

        entry = ctk.CTkEntry(
            parent,
            height=HEIGHT_ENTRY,
            corner_radius=10,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_BORDER,
            border_width=1,
            placeholder_text=placeholder,
            placeholder_text_color=COLOR_TEXT_MUTED,
            font=("Segoe UI", 13),
            text_color=COLOR_TEXT
        )
        entry.grid(
            row=row + 1, column=col, columnspan=colspan,
            sticky="ew", padx=12, pady=(4, 2)
        )

        # Focus states — borda laranja ao focar
        entry.bind("<FocusIn>", lambda e, en=entry: en.configure(border_color=COLOR_PRIMARY))
        entry.bind("<FocusOut>", lambda e, en=entry: en.configure(border_color=COLOR_BORDER))

        return entry

    def _criar_header_secao(self, parent, titulo, row):
        """Cria um header de seção com accent bar lateral."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(SPACING_FIELD_Y + 6, 2))

        accent = ctk.CTkFrame(
            frame,
            width=4,
            height=18,
            fg_color=COLOR_PRIMARY,
            corner_radius=2
        )
        accent.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            frame,
            text=titulo.upper(),
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(side="left")

    # ============================================================
    # CAMPOS — lógica de formulário (preservada)
    # ============================================================
    def atualizar_campos(self, tipo):
        for w in self.frame_campos.winfo_children():
            w.destroy()
        self.campos.clear()

        # Atualizar título
        self.section_title_label.configure(text=f"FORMULÁRIO  ›  {tipo.upper()}")

        # Definição de placeholders por campo
        placeholders = {
            "Nome": "Nome completo do colaborador",
            "CPF": "000.000.000-00",
            "Setor/Cargo": "Ex: TI / Analista",
            "Empresa": "Nome da empresa",
            "Descrição do Equipamento": "Ex: Notebook Dell Latitude",
            "Marca/Modelo": "Ex: Dell / Latitude 5520",
            "Série": "Número de série",
            "Patrimônio": "Código do patrimônio",
            "Estado do equipamento": "Novo, Usado, Recondicionado...",
            "Técnico responsável": "Nome do técnico",
            "Cargo": "Cargo do colaborador",
            "Departamento": "Departamento / Setor",
            "Número da Linha": "Ex: (41) 99999-0000",
        }

        if tipo == "Equipamento":
            sections = [
                ("Colaborador", [
                    ("Nome", "CPF"),
                    ("Setor/Cargo", "Empresa")
                ]),
                ("Equipamento", [
                    ("Descrição do Equipamento", "Marca/Modelo"),
                    ("Série", "Patrimônio"),
                    ("Estado do equipamento", None),
                    ("Técnico responsável", None)
                ])
            ]
        elif tipo == "VPN":
            sections = [("VPN", [("Nome", "Cargo"), ("Departamento", None)])]

        elif tipo == "Telecom":
            sections = [
                ("Colaborador", [
                    ("Nome", "CPF"),
                    ("Setor/Cargo", "Empresa")
                ]),
                ("Equipamento", [
                    ("Descrição do Equipamento", "Marca/Modelo"),
                    ("Série", "Número da Linha"),
                    ("Técnico responsável", None)
                ])]
        else:
            sections = [("Administrador Local", [("Nome", "CPF")])]

        row = 0
        for title, fields in sections:
            self._criar_header_secao(self.frame_campos, title, row)
            row += 1
            for f1, f2 in fields:
                if f2:
                    e1 = self._criar_campo(
                        self.frame_campos, f1,
                        placeholder=placeholders.get(f1, ""),
                        row=row, col=0
                    )
                    self.campos[f1] = e1

                    e2 = self._criar_campo(
                        self.frame_campos, f2,
                        placeholder=placeholders.get(f2, ""),
                        row=row, col=1
                    )
                    self.campos[f2] = e2
                else:
                    e1 = self._criar_campo(
                        self.frame_campos, f1,
                        placeholder=placeholders.get(f1, ""),
                        row=row, col=0, colspan=2
                    )
                    self.campos[f1] = e1
                row += 2

    # ============================================================
    # 🔴 FEEDBACK VISUAL — campos vazios
    # ============================================================
    def _destacar_campos_vazios(self, dados):
        """Destaca com borda vermelha os campos que estão vazios."""
        tem_vazio = False
        for nome, entry in self.campos.items():
            valor = dados.get(nome, "")
            if not valor:
                entry.configure(border_color=COLOR_ERROR, border_width=2)
                tem_vazio = True
            else:
                entry.configure(border_color=COLOR_BORDER, border_width=1)
        return tem_vazio

    def _resetar_bordas(self):
        """Remove destaque vermelho de todos os campos."""
        for entry in self.campos.values():
            entry.configure(border_color=COLOR_BORDER, border_width=1)

    # ============================================================
    # THREAD DO PROCESSAMENTO (lógica preservada)
    # ============================================================
    def executar_processo_thread(self):
        dados = {k: e.get().strip() for k, e in self.campos.items()}

        # Validação com feedback visual
        if self._destacar_campos_vazios(dados):
            self._mostrar_toast(
                "⚠️  Preencha todos os campos destacados",
                tipo="warning"
            )
            return

        self._resetar_bordas()

        # Desabilitar botão durante processamento
        self.btn_submit.configure(
            state="disabled",
            text="  ⏳  GERANDO...",
            fg_color=COLOR_TEXT_MUTED
        )

        # Mostrar progress bar na status bar
        self.progress_bar.pack(side="left", padx=(20, 0), pady=8)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        threading.Thread(target=self.executar_processo, daemon=True).start()

    def executar_processo(self):
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass

        tipo = self.tipo_selecionado
        dados = {k: e.get().strip() for k, e in self.campos.items()}

        try:
            gerador = GeradorDeTermos()
            if tipo == "Equipamento":
                pdf = gerador.preencher_termo_equipamento(
                    nome=dados["Nome"], cpf=dados["CPF"], setor=dados["Setor/Cargo"],
                    empresa=dados["Empresa"], equipamento=dados["Descrição do Equipamento"],
                    marca=dados["Marca/Modelo"], serie=dados["Série"],
                    patrimonio=dados["Patrimônio"], estadoequip=dados["Estado do equipamento"],
                    tecnico=dados['Técnico responsável']
                )

            elif tipo == "Telecom":
                pdf = gerador.preencher_termo_telecom(
                    nome=dados["Nome"], cpf=dados["CPF"], setor=dados["Setor/Cargo"],
                    empresa=dados["Empresa"], equipamento=dados["Descrição do Equipamento"],
                    marca=dados["Marca/Modelo"], serie=dados["Série"],
                    numero=dados["Número da Linha"], tecnico=dados['Técnico responsável']
                )

            elif tipo == "VPN":
                pdf = gerador.preencher_termo_vpn(dados["Nome"], dados["Cargo"], dados["Departamento"])
            else:
                pdf = gerador.preencher_termo_adm(dados["Nome"], dados["CPF"])

            pasta_drive = localizar_pasta_drive_usuario(self.nome_drive)
            destino = mover_para_pasta_drive(pdf, pasta_drive)

            # Toast de sucesso
            self.after(0, lambda: self._mostrar_toast(
                f"✅  Termo gerado e enviado para: {destino.name}",
                tipo="success",
                duracao=6000
            ))

        except Exception as e:
            self.after(0, lambda: self._mostrar_toast(
                f"❌  Erro: {e}",
                tipo="error",
                duracao=8000
            ))
        finally:
            self.after(0, self._finalizar_processo)
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

    def _finalizar_processo(self):
        """Restaura a interface após o processamento."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_submit.configure(
            state="normal",
            text="  🚀  GERAR E ENVIAR TERMO",
            fg_color=COLOR_PRIMARY
        )


# ============================================================
# 🏁 EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    app = App()
    app.mainloop()
