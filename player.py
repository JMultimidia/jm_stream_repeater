import tkinter as tk
from tkinter import ttk
import vlc
import time
from datetime import datetime, time as dt_time, timedelta
import threading
import json
import os


class StreamPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Player")

        # Configuração do VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.is_playing = False
        self.scheduled_thread = None
        self.should_stop = False
        self.blink_state = False

        # Configurações padrão
        self.config = {
            'stream_url': 'http://exemplo.com/stream',
            'auto_start_time': '19:00',
            'auto_stop_time': '20:00'
        }

        # Criar interface primeiro
        self.create_widgets()

        # Depois carregar configurações
        self.config_file = 'stream_config.json'
        self.load_config()

        # Iniciar verificação de agendamento
        self.start_schedule()

        # Iniciar atualização do countdown
        self.update_countdown()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    # Atualizar campos da interface
                    self.url_entry.delete(0, tk.END)
                    self.url_entry.insert(0, self.config['stream_url'])
                    self.start_time.delete(0, tk.END)
                    self.start_time.insert(0, self.config['auto_start_time'])
                    self.stop_time.delete(0, tk.END)
                    self.stop_time.insert(0, self.config['auto_stop_time'])
            except json.JSONDecodeError:
                self.save_config()
        else:
            self.save_config()

    def save_config(self):
        try:
            self.config['stream_url'] = self.url_entry.get()
            self.config['auto_start_time'] = self.start_time.get()
            self.config['auto_stop_time'] = self.stop_time.get()

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
            self.status_label.config(text="Status: Configurações salvas")
        except Exception as e:
            self.status_label.config(text=f"Erro ao salvar: {str(e)}")

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL do Stream
        ttk.Label(main_frame, text="URL do Stream:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, pady=5)
        self.url_entry.insert(0, self.config['stream_url'])

        # Botão Salvar Configurações
        ttk.Button(main_frame, text="Salvar Configurações", command=self.save_config).grid(row=1, column=0,
                                                                                           columnspan=3, pady=5)

        # Horários automáticos
        ttk.Label(main_frame, text="Início Auto (HH:MM:SS):").grid(row=2, column=0, sticky=tk.W)
        self.start_time = ttk.Entry(main_frame, width=10)
        self.start_time.grid(row=2, column=1, sticky=tk.W)
        self.start_time.insert(0, self.config['auto_start_time'])

        ttk.Label(main_frame, text="Fim Auto (HH:MM:SS):").grid(row=3, column=0, sticky=tk.W)
        self.stop_time = ttk.Entry(main_frame, width=10)
        self.stop_time.grid(row=3, column=1, sticky=tk.W)
        self.stop_time.insert(0, self.config['auto_stop_time'])

        # Botões de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=5)
        ttk.Button(control_frame, text="Play", command=self.play).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop).grid(row=0, column=1, padx=5)

        # Frame para o countdown
        self.countdown_frame = tk.Frame(main_frame, relief=tk.RAISED, borderwidth=1)
        self.countdown_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        self.countdown_label = ttk.Label(
            self.countdown_frame,
            text="Próxima reprodução em: --:--:--",
            font=('Arial', 14, 'bold'),
            padding=10
        )
        self.countdown_label.pack(fill=tk.X)

        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Parado")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

        # Bind para salvar ao pressionar Enter nos campos
        self.url_entry.bind('<Return>', lambda e: self.save_config())
        self.start_time.bind('<Return>', lambda e: self.save_config())
        self.stop_time.bind('<Return>', lambda e: self.save_config())

    def get_next_stream_time(self):
        try:
            now = datetime.now()
            start_time = dt_time.fromisoformat(self.start_time.get())
            start_datetime = datetime.combine(now.date(), start_time)

            # Se o horário já passou hoje, considera o próximo dia
            if start_datetime < now:
                start_datetime = datetime.combine(now.date() + timedelta(days=1), start_time)

            return start_datetime
        except ValueError:
            return None

    def update_countdown(self):
        if not self.is_playing:
            next_stream = self.get_next_stream_time()
            if next_stream:
                time_diff = next_stream - datetime.now()
                if time_diff.total_seconds() > 0:
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    seconds = int(time_diff.total_seconds() % 60)
                    countdown_text = f"Próxima reprodução em: {hours:02d}:{minutes:02d}:{seconds:02d}"

                    # Definir cores baseado no tempo restante
                    if time_diff.total_seconds() <= 30:  # Últimos 30 segundos
                        if self.blink_state:
                            self.countdown_frame.configure(bg='red')
                            self.countdown_label.configure(background='red', foreground='white')
                        else:
                            self.countdown_frame.configure(bg='yellow')
                            self.countdown_label.configure(background='yellow', foreground='black')
                        self.blink_state = not self.blink_state
                    elif time_diff.total_seconds() <= 300:  # Últimos 5 minutos
                        self.countdown_frame.configure(bg='yellow')
                        self.countdown_label.configure(background='yellow', foreground='black')
                    else:
                        self.countdown_frame.configure(bg='white')
                        self.countdown_label.configure(background='white', foreground='black')
                else:
                    countdown_text = "Iniciando a reprodução..."
            else:
                countdown_text = "Horário inválido"
        else:
            countdown_text = "Tocando..."
            self.countdown_frame.configure(bg='green')
            self.countdown_label.configure(background='green', foreground='white')

        self.countdown_label.configure(text=countdown_text)
        self.root.after(500, self.update_countdown)  # Atualiza a cada 500ms

    def play(self):
        if not self.is_playing:
            url = self.url_entry.get()
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True
            self.status_label.config(text="Status: Reproduzindo")
            self.countdown_frame.configure(bg='green')
            self.countdown_label.configure(background='green', foreground='white')

    def stop(self):
        if self.is_playing:
            self.player.stop()
            self.is_playing = False
            self.status_label.config(text="Status: Parado")
            self.countdown_frame.configure(bg='white')
            self.countdown_label.configure(background='white', foreground='black')

    def check_schedule(self):
        while not self.should_stop:
            try:
                current_time = datetime.now()
                start_time = dt_time.fromisoformat(self.start_time.get())
                stop_time = dt_time.fromisoformat(self.stop_time.get())

                current_datetime = current_time
                start_datetime = datetime.combine(current_time.date(), start_time)
                stop_datetime = datetime.combine(current_time.date(), stop_time)

                # Verifica se está dentro do horário programado
                if start_datetime <= current_datetime < stop_datetime:
                    if not self.is_playing:
                        self.root.after(0, self.play)
                        print(f"Iniciando reprodução automática: {current_time}")
                elif self.is_playing:
                    self.root.after(0, self.stop)
                    print(f"Parando reprodução automática: {current_time}")

                # Espera até o próximo segundo
                time.sleep(0.1)  # Verifica a cada 100ms para maior precisão

            except ValueError as e:
                print(f"Erro no formato do horário: {e}")
            except Exception as e:
                print(f"Erro na verificação do agendamento: {e}")

    def start_schedule(self):
        if not self.scheduled_thread or not self.scheduled_thread.is_alive():
            self.should_stop = False
            self.scheduled_thread = threading.Thread(target=self.check_schedule)
            self.scheduled_thread.daemon = True
            self.scheduled_thread.start()
            self.status_label.config(text="Status: Agendamento ativado")
            print("Agendamento iniciado")

    def on_closing(self):
        self.should_stop = True
        if self.scheduled_thread:
            self.scheduled_thread.join(timeout=1)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StreamPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()