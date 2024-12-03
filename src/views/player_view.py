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
        self.root.grid_rowconfigure(1, weight=1)  # Row 1 porque row 0 será o menu
        self.root.grid_columnconfigure(0, weight=1)

        # Carrega ícones
        self.load_icons()

        # Cria o menu
        self._create_menu()

        # Cria os frames principais
        self._create_frames()

        # Cria a interface principal
        self._setup_main_ui()

        # Cria a interface de configuração
        self._setup_config_ui()

        # Inicia mostrando a tela principal
        self.show_main_screen()

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

    def _create_menu(self):
        """Cria a barra de menu superior"""
        self.menu_bar = ctk.CTkFrame(self.root, fg_color="#2B2B2B", height=25)
        self.menu_bar.grid(row=0, column=0, sticky="ew")
        self.menu_bar.grid_columnconfigure(2, weight=1)

        # Menu Arquivo
        self.file_menu = ctk.CTkButton(
            self.menu_bar,
            text="Arquivo",
            width=60,
            height=25,
            fg_color="transparent",
            hover_color="#404040",
            command=self._show_file_menu
        )
        self.file_menu.grid(row=0, column=0, padx=2)

        # Menu Ferramentas
        self.tools_menu = ctk.CTkButton(
            self.menu_bar,
            text="Ferramentas",
            width=90,
            height=25,
            fg_color="transparent",
            hover_color="#404040",
            command=self._show_tools_menu
        )
        self.tools_menu.grid(row=0, column=1, padx=2)

        # Inicializa variável para controle do menu atual
        self.active_menu = None

    def _show_file_menu(self, event=None):
        """Mostra o menu dropdown de arquivo"""
        # Se o menu atual for o de arquivo, fecha e retorna
        if self.active_menu == 'file':
            self._close_menu()
            return

        # Fecha qualquer menu aberto
        self._close_menu()

        # Cria novo menu
        menu = ctk.CTkFrame(self.root, fg_color="#2B2B2B", border_width=1)
        menu.place(x=self.file_menu.winfo_rootx(),
                   y=self.file_menu.winfo_rooty() + self.file_menu.winfo_height())

        # Opção Sair
        ctk.CTkButton(
            menu,
            text="Sair",
            width=100,
            height=25,
            fg_color="transparent",
            hover_color="#404040",
            command=self.root.quit
        ).pack(fill="x", pady=1)

        # Atualiza referências do menu atual
        self.current_menu = menu
        self.active_menu = 'file'
        self._bind_menu_close()

    def _show_tools_menu(self):
        """Mostra o menu dropdown de ferramentas"""
        # Se o menu atual for o de ferramentas, fecha e retorna
        if self.active_menu == 'tools':
            self._close_menu()
            return

        # Fecha qualquer menu aberto
        self._close_menu()

        # Cria novo menu
        menu = ctk.CTkFrame(self.root, fg_color="#2B2B2B", border_width=1)
        menu.place(x=self.tools_menu.winfo_rootx(),
                   y=self.tools_menu.winfo_rooty() + self.file_menu.winfo_height())

        # Opção Configurações de Áudio
        ctk.CTkButton(
            menu,
            text="Configurações de Áudio",
            width=180,
            height=25,
            fg_color="transparent",
            hover_color="#404040",
            command=lambda: self._show_config_from_menu(menu)
        ).pack(fill="x", pady=1)

        self.current_menu = menu
        self.active_menu = 'tools'
        self._bind_menu_close()

    def _close_menu(self):
        """Fecha o menu dropdown atual"""
        if hasattr(self, 'current_menu') and self.current_menu.winfo_exists():
            self.current_menu.destroy()
        self.active_menu = None
        # Remove o binding de forma segura
        try:
            if hasattr(self, '_menu_bind_id'):
                self.root.unbind('<Button-1>', self._menu_bind_id)
                delattr(self, '_menu_bind_id')
        except Exception as e:
            print(f"Aviso: Não foi possível remover binding: {e}")

    def _bind_menu_close(self):
        """Configura o binding para fechar o menu ao clicar fora"""
        # Remove binding anterior se existir
        if hasattr(self, '_menu_bind_id'):
            try:
                self.root.unbind('<Button-1>', self._menu_bind_id)
            except:
                pass

        def close_menu(event):
            # Verifica se o clique foi fora do menu e não em um botão do menu principal
            if (event.widget != self.current_menu and
                    event.widget != self.file_menu and
                    event.widget != self.tools_menu):
                self._close_menu()

        # Guarda o ID do novo binding
        self._menu_bind_id = self.root.bind('<Button-1>', close_menu)

    def _show_config_from_menu(self, menu):
        """Mostra a tela de configuração mantendo o tamanho da janela"""
        # Fecha o menu
        menu.destroy()

        # Salva o tamanho atual da janela
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()

        # Oculta frame principal e mostra configurações
        self.main_frame.grid_remove()
        self.config_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Força o tamanho da janela a permanecer o mesmo
        self.root.geometry(f"{current_width}x{current_height}")

        # Carrega os dispositivos
        self._load_audio_devices()

    def show_main_screen(self):
        """Mostra a tela principal mantendo o tamanho da janela"""
        # Salva o tamanho atual da janela
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()

        # Troca os frames
        self.config_frame.grid_remove()
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Força o tamanho da janela a permanecer o mesmo
        self.root.geometry(f"{current_width}x{current_height}")

    def _create_frames(self):
        """Cria os frames principais da aplicação"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Frame de configurações
        self.config_frame = ctk.CTkFrame(self.root)
        self.config_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def _setup_main_ui(self):
        """Configura a interface principal"""
        self.main_frame.grid_columnconfigure(0, weight=1)

        # URL do Stream
        self._create_url_section()

        # Horários
        self._create_time_section()

        # Botão Salvar
        self._create_save_button()

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

    def _setup_config_ui(self):
        """Configura a interface da tela de configurações"""
        # Título
        ctk.CTkLabel(
            self.config_frame,
            text="Configurações de Áudio",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        # Frame para dispositivos
        device_frame = ctk.CTkFrame(self.config_frame)
        device_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            device_frame,
            text="Dispositivo de Saída:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)

        # Combobox para dispositivos
        self.device_var = ctk.StringVar()
        self.device_combo = ctk.CTkOptionMenu(
            device_frame,
            variable=self.device_var,
            values=["Carregando dispositivos..."],
            width=300
        )
        self.device_combo.pack(pady=10)

        # Botões
        button_frame = ctk.CTkFrame(self.config_frame)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Salvar",
            command=self._save_audio_config,
            fg_color="#2B7539",
            hover_color="#1E5C2C"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Voltar",
            command=self.show_main_screen
        ).pack(side="left", padx=5)

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
        self.save_button.grid(row=2, column=0, columnspan=3, pady=10)

    def _create_time_section(self):
        """Cria seção de configuração de horários"""
        time_frame = ctk.CTkFrame(self.main_frame)
        time_frame.grid(row=1, column=0, columnspan=3, pady=5)

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

    def show_main_screen(self):
        """Mostra a tela principal"""
        self.config_frame.grid_remove()
        self.main_frame.grid()

    def show_config_screen(self):
        """Mostra a tela de configurações"""
        self.main_frame.grid_remove()
        self.config_frame.grid()
        self._load_audio_devices()

    def _load_audio_devices(self):
        """Carrega a lista de dispositivos de áudio"""
        devices = self._get_callback('get_devices')()
        current_device = self._get_callback('get_current_device')()

        # Atualiza o combobox
        device_names = [d['name'] for d in devices]
        self.device_combo.configure(values=device_names)

        # Guarda referência dos devices
        self.devices = {d['name']: d['id'] for d in devices}

        # Seleciona o dispositivo atual
        for device in devices:
            if device['id'] == current_device:
                self.device_var.set(device['name'])
                break

    def _save_audio_config(self):
        """Salva a configuração de áudio"""
        selected_name = self.device_var.get()
        device_id = self.devices.get(selected_name, '')
        if self._get_callback('save_device')(device_id):
            self.show_main_screen()

    def _show_file_menu(self):
        """Mostra o menu dropdown de arquivo"""
        # Menu dropdown personalizado
        menu = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
        menu.place(x=self.file_menu.winfo_rootx(),
                   y=self.file_menu.winfo_rooty() + self.file_menu.winfo_height())

        # Opção Sair
        ctk.CTkButton(
            menu,
            text="Sair",
            width=60,
            height=25,
            fg_color="transparent",
            hover_color="#404040",
            command=self.root.quit
        ).pack(fill="x", pady=1)

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

    def set_callback_getter(self, callback_getter):
        """Define a função para obter callbacks"""
        self._get_callback = callback_getter