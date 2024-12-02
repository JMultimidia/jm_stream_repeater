import customtkinter as ctk
from datetime import datetime
from PIL import Image
import io
import base64
from ..utils.icons import PlayerIcons
from .volume_view import VolumeView


class PlayerView:
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Player")

        # Configurações da janela
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Carrega ícones
        self.load_icons()

        # Cria a interface
        self._setup_ui()

    def load_icons(self):
        """Carrega e prepara os ícones para os botões"""
        try:
            icons = PlayerIcons()

            # Decodifica e carrega o ícone de play
            play_data = base64.b64decode(icons.PLAY_ICON)
            play_image = Image.open(io.BytesIO(play_data))
            self.play_icon = ctk.CTkImage(
                light_image=play_image,
                dark_image=play_image,
                size=(80, 80)
            )

            # Decodifica e carrega o ícone de stop
            stop_data = base64.b64decode(icons.STOP_ICON)
            stop_image = Image.open(io.BytesIO(stop_data))
            self.stop_icon = ctk.CTkImage(
                light_image=stop_image,
                dark_image=stop_image,
                size=(80, 80)
            )

        except Exception as e:
            print(f"Erro ao carregar ícones: {e}")
            self.play_icon = None
            self.stop_icon = None

    def _setup_ui(self):
        """Configura todos os elementos da interface"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # URL do Stream
        self._create_url_section()

        # Botão Salvar
        self._create_save_button()

        # Horários
        self._create_time_section()

        # Relógio
        self._create_clock_section()

        # Controles
        self._create_control_section()

        # Countdown
        self._create_countdown_section()

        # Status
        self._create_status_section()

        # Volume
        self.setup_volume_control()

    def _create_url_section(self):
        """Cria seção da URL do stream"""
        ctk.CTkLabel(
            self.main_frame,
            text="URL do Stream:"
        ).grid(row=0, column=0, sticky="w")

        self.url_entry = ctk.CTkEntry(self.main_frame, width=400)
        self.url_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5)
        self.url_entry.bind('<Return>', lambda e: self.save_button.invoke())

    def _create_save_button(self):
        """Cria botão de salvar configurações"""
        self.save_button = ctk.CTkButton(
            self.main_frame,
            text="Salvar Configurações",
            fg_color="#2B7539",
            hover_color="#1E5C2C"
        )
        self.save_button.grid(row=1, column=0, columnspan=3, pady=10)

    def _create_time_section(self):
        """Cria seção de configuração de horários"""
        time_frame = ctk.CTkFrame(self.main_frame)
        time_frame.grid(row=2, column=0, columnspan=3, pady=5)

        # Horário de início
        ctk.CTkLabel(
            time_frame,
            text="Início (HH:MM:SS):"
        ).grid(row=0, column=0, padx=5)

        self.start_time = ctk.CTkEntry(time_frame, width=100)
        self.start_time.grid(row=0, column=1, padx=5)
        self.start_time.bind('<Return>', lambda e: self.save_button.invoke())

        # Horário de fim
        ctk.CTkLabel(
            time_frame,
            text="Fim (HH:MM:SS):"
        ).grid(row=0, column=2, padx=5)

        self.stop_time = ctk.CTkEntry(time_frame, width=100)
        self.stop_time.grid(row=0, column=3, padx=5)
        self.stop_time.bind('<Return>', lambda e: self.save_button.invoke())

    def _create_clock_section(self):
        """Cria seção do relógio"""
        self.clock_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#1a1a1a"
        )
        self.clock_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        self.clock_label = ctk.CTkLabel(
            self.clock_frame,
            text="--:--:--",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#ffffff"
        )
        self.clock_label.pack(pady=10)

    def _create_control_section(self):
        """Cria seção dos botões de controle"""
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=10)

        # Botão Play
        self.play_button = ctk.CTkButton(
            control_frame,
            text="",
            image=self.play_icon,
            width=80,
            height=80,
            fg_color="#1a1a1a",
            hover_color="#2b2b2b",
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
            fg_color="#1a1a1a",
            hover_color="#2b2b2b",
            border_width=0
        )
        self.stop_button.grid(row=0, column=1, padx=10)

    def _create_countdown_section(self):
        """Cria seção do countdown"""
        self.countdown_frame = ctk.CTkFrame(self.main_frame)
        self.countdown_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")

        self.countdown_label = ctk.CTkLabel(
            self.countdown_frame,
            text="Próxima reprodução em: --:--:--",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.countdown_label.pack(pady=10)

    def _create_status_section(self):
        """Cria seção de status"""
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Status: Parado"
        )
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

    def setup_volume_control(self):
        """Inicializa o controle de volume"""
        self.volume_view = VolumeView(self.main_frame)
        self.volume_view.get_frame().grid(row=7, column=0, columnspan=3, pady=5)

    def setup_bindings(self, play_callback, stop_callback, save_callback):
        """Configura os callbacks dos botões"""
        self.play_button.configure(command=play_callback)
        self.stop_button.configure(command=stop_callback)
        self.save_button.configure(command=save_callback)

    def update_config_fields(self, config):
        """Atualiza os campos com as configurações carregadas"""
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, config['stream_url'])

        self.start_time.delete(0, "end")
        self.start_time.insert(0, config['auto_start_time'])

        self.stop_time.delete(0, "end")
        self.stop_time.insert(0, config['auto_stop_time'])

    def get_config_data(self):
        """Retorna os dados atuais dos campos de configuração"""
        return {
            'stream_url': self.url_entry.get(),
            'auto_start_time': self.start_time.get(),
            'auto_stop_time': self.stop_time.get()
        }

    def get_stream_url(self):
        """Retorna a URL do stream"""
        return self.url_entry.get()

    def update_status(self, message):
        """Atualiza a mensagem de status"""
        self.status_label.configure(text=f"Status: {message}")

    def update_player_state(self, is_playing):
        """Atualiza o estado visual do player"""
        if is_playing:
            self.countdown_frame.configure(fg_color="#28a745")
            self.countdown_label.configure(text_color="white")
        else:
            self.countdown_frame.configure(fg_color="#f8f9fa")
            self.countdown_label.configure(text_color="black")

    def start_clock_update(self):
        """Inicia a atualização do relógio"""

        def update_clock():
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                self.clock_label.configure(text=current_time)
            except Exception as e:
                print(f"Erro ao atualizar relógio: {e}")
            finally:
                self.root.after(1000, update_clock)

        update_clock()

    def start_countdown_update(self, countdown_callback):
        """Inicia a atualização do countdown"""

        def update_countdown():
            try:
                countdown_info = countdown_callback()
                if countdown_info:
                    self.countdown_frame.configure(fg_color=countdown_info['color'])
                    self.countdown_label.configure(
                        text=countdown_info['text'],
                        text_color=countdown_info['text_color']
                    )
            except Exception as e:
                print(f"Erro ao atualizar countdown: {e}")
            finally:
                self.root.after(500, update_countdown)

        update_countdown()