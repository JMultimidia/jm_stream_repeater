import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import vlc
from datetime import datetime
import os
from PIL import Image, ImageTk
import base64
import io
from player_methods import PlayerMethods


class StreamPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Player")

        # Configura o tema do customtkinter
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Inicializa os métodos
        self.methods = PlayerMethods(self)

        # Configurações padrão
        self.config = {
            'stream_url': 'http://exemplo.com/stream',
            'auto_start_time': '19:00:00',
            'auto_stop_time': '20:00:00'
        }

        # Carregar ícones
        self.load_icons()

        # Criar interface
        self.create_widgets()

        # Carregar configurações
        self.config_file = 'stream_config.json'
        self.methods.load_config()

        # Iniciar verificação de agendamento e countdown
        self.methods.start_schedule()
        self.methods.update_clock()
        self.methods.update_countdown()

    def load_icons(self):
        try:
            play_data = base64.b64decode(self.methods.PLAY_ICON)
            stop_data = base64.b64decode(self.methods.STOP_ICON)

            play_image = Image.open(io.BytesIO(play_data))
            stop_image = Image.open(io.BytesIO(stop_data))

            # Usar CTkImage em vez de PhotoImage
            self.play_icon = ctk.CTkImage(light_image=play_image, dark_image=play_image, size=(80, 80))
            self.stop_icon = ctk.CTkImage(light_image=stop_image, dark_image=stop_image, size=(80, 80))

        except Exception as e:
            print(f"Erro ao carregar ícones: {e}")
            self.play_icon = None
            self.stop_icon = None

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # URL do Stream
        ctk.CTkLabel(main_frame, text="URL do Stream:").grid(row=0, column=0, sticky="w")
        self.url_entry = ctk.CTkEntry(main_frame, width=400)
        self.url_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5)
        self.url_entry.insert(0, self.config['stream_url'])

        # Botão Salvar
        ctk.CTkButton(
            main_frame,
            text="Salvar Configurações",
            command=self.methods.save_config,
            fg_color="#2B7539",
            hover_color="#1E5C2C"
        ).grid(row=1, column=0, columnspan=3, pady=10)

        # Horários
        time_frame = ctk.CTkFrame(main_frame)
        time_frame.grid(row=2, column=0, columnspan=3, pady=5)

        ctk.CTkLabel(time_frame, text="Início (HH:MM:SS):").grid(row=0, column=0, padx=5)
        self.start_time = ctk.CTkEntry(time_frame, width=100)
        self.start_time.grid(row=0, column=1, padx=5)
        self.start_time.insert(0, self.config['auto_start_time'])

        ctk.CTkLabel(time_frame, text="Fim (HH:MM:SS):").grid(row=0, column=2, padx=5)
        self.stop_time = ctk.CTkEntry(time_frame, width=100)
        self.stop_time.grid(row=0, column=3, padx=5)
        self.stop_time.insert(0, self.config['auto_stop_time'])

        # Container do Relógio
        clock_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a")  # Fundo escuro
        clock_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        self.clock_label = ctk.CTkLabel(
            clock_frame,
            text="--:--:--",
            font=ctk.CTkFont(size=32, weight="bold"),  # Fonte maior
            text_color="#ffffff"  # Texto branco
        )
        self.clock_label.pack(pady=10)

        # Frame para botões de controle
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=10)

        # Botão Play
        self.play_button = ctk.CTkButton(
            control_frame,
            text="",
            image=self.play_icon,
            width=80,
            height=80,
            fg_color="#1a1a1a",  # Cor de fundo escura que combina com o tema
            hover_color="#2b2b2b",  # Um pouco mais claro no hover
            command=self.methods.play,
            border_width=0
        )
        self.play_button.grid(row=0, column=0, padx=10)

        # Botão Stop
        self.stop_button = ctk.CTkButton(
            control_frame,
            text="",
            image=self.stop_icon,
            width=80,
            height=80,
            fg_color="#1a1a1a",  # Cor de fundo escura que combina com o tema
            hover_color="#2b2b2b",  # Um pouco mais claro no hover
            command=self.methods.stop,
            border_width=0
        )
        self.stop_button.grid(row=0, column=1, padx=10)

        # Frame para o countdown
        self.countdown_frame = ctk.CTkFrame(main_frame)
        self.countdown_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")

        # Separador
        separator = ctk.CTkFrame(self.countdown_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=5)

        self.countdown_label = ctk.CTkLabel(
            self.countdown_frame,
            text="Próxima reprodução em: --:--:--",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.countdown_label.pack(pady=10)

        # Status
        self.status_label = ctk.CTkLabel(main_frame, text="Status: Parado")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

        # Configurar expansão da grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Bindings
        self.url_entry.bind('<Return>', lambda e: self.methods.save_config())
        self.start_time.bind('<Return>', lambda e: self.methods.save_config())
        self.stop_time.bind('<Return>', lambda e: self.methods.save_config())


if __name__ == "__main__":
    root = ctk.CTk()
    app = StreamPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.methods.on_closing)
    root.mainloop()