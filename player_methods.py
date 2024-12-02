import vlc
import time
from datetime import datetime, time as dt_time, timedelta
import threading
import json
import os


class PlayerMethods:
    def __init__(self, player):
        self.player = player
        self.instance = None
        self.media_player = None
        self.initialize_vlc()

        # Estado do player
        self.is_playing = False
        self.manual_play = False
        self.manual_stop = False
        self.scheduled_thread = None
        self.should_stop = False
        self.blink_state = False

        # Ícones em Base64 - Mantenha seus ícones atuais aqui
        self.PLAY_ICON = '''
        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
        '''
        self.STOP_ICON = '''
        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
        '''

    def initialize_vlc(self):
        """Inicializa o player VLC com configurações otimizadas"""
        try:
            # Adicionado --quiet para reduzir mensagens de log e --aout=pulse para melhor compatibilidade
            self.instance = vlc.Instance('--no-xlib --quiet --aout=pulse')
            self.media_player = self.instance.media_player_new()
            print("VLC inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar VLC: {e}")
            self.instance = None
            self.media_player = None

    def ensure_vlc_initialized(self):
        """Garante que o VLC está inicializado antes de usar"""
        if self.instance is None or self.media_player is None:
            self.initialize_vlc()
            if self.instance is None or self.media_player is None:
                raise Exception("Não foi possível inicializar o VLC")

    def start_playback(self, manual=False):
        """Função central para iniciar a reprodução"""
        try:
            self.ensure_vlc_initialized()
            url = self.player.url_entry.get()

            if not url:
                raise ValueError("URL do stream não pode estar vazia")

            # Cria nova mídia e configura network caching para melhor buffering
            media = self.instance.media_new(url)
            media.add_option('--network-caching=1000')

            if not media:
                raise ValueError("Não foi possível criar mídia a partir da URL")

            self.media_player.set_media(media)
            self.media_player.video_set_scale(0)  # Desativa saída de vídeo
            result = self.media_player.play()

            if result == 0:
                self.is_playing = True
                self.manual_play = manual
                play_type = "Manual" if manual else "Agendado"
                self.player.status_label.configure(text=f"Status: Reproduzindo ({play_type})")
                self.player.countdown_frame.configure(fg_color="#28a745")
                self.player.countdown_label.configure(text_color="white")
                return True
            else:
                raise Exception(f"Erro ao iniciar reprodução: código {result}")

        except Exception as e:
            print(f"Erro ao iniciar reprodução: {e}")
            self.player.status_label.configure(text=f"Status: Erro - {str(e)}")
            self.is_playing = False
            self.manual_play = False
            self.initialize_vlc()
            return False

    def play(self):
        """Inicia reprodução manual"""
        if not self.is_playing:
            if self.start_playback(manual=True):
                print("Reprodução manual iniciada com sucesso")
            else:
                print("Falha ao iniciar reprodução manual")

    def stop(self):
        """Para a reprodução"""
        try:
            if self.is_playing and self.media_player:
                self.media_player.stop()
                self.is_playing = False
                self.manual_play = False
                self.manual_stop = True
                self.player.status_label.configure(text="Status: Parado manualmente")
                self.player.countdown_frame.configure(fg_color="#f8f9fa")
                self.player.countdown_label.configure(text_color="black")
                print("Reprodução interrompida manualmente")
        except Exception as e:
            print(f"Erro ao parar: {e}")
            self.player.status_label.configure(text=f"Status: Erro ao parar - {str(e)}")
            self.is_playing = False
            self.manual_play = False
            self.manual_stop = False
            self.initialize_vlc()

    def check_schedule(self):
        """Verifica o agendamento de reprodução"""
        while not self.should_stop:
            try:
                current_time = datetime.now()
                start_time = dt_time.fromisoformat(self.player.start_time.get())
                stop_time = dt_time.fromisoformat(self.player.stop_time.get())

                current_datetime = current_time
                start_datetime = datetime.combine(current_time.date(), start_time)
                stop_datetime = datetime.combine(current_time.date(), stop_time)

                # Ajusta para caso o horário de parada seja no dia seguinte
                if stop_time < start_time:
                    if current_datetime.time() < start_time:
                        stop_datetime = datetime.combine(current_time.date(), stop_time)
                    else:
                        stop_datetime = datetime.combine(current_time.date() + timedelta(days=1), stop_time)

                # Verifica se está no período agendado e não foi parado manualmente
                if start_datetime <= current_datetime < stop_datetime and not self.manual_stop:
                    if not self.is_playing:
                        print(f"Iniciando reprodução agendada: {current_datetime}")
                        self.player.root.after(0, lambda: self.start_playback(manual=False))
                elif current_datetime >= stop_datetime:
                    # Reseta o manual_stop quando passar do horário de parada
                    self.manual_stop = False
                    if self.is_playing and not self.manual_play:
                        print(f"Parando reprodução agendada: {current_datetime}")
                        self.player.root.after(0, self.stop)

                time.sleep(0.1)

            except ValueError as e:
                print(f"Erro no formato do horário: {e}")
            except Exception as e:
                print(f"Erro na verificação do agendamento: {e}")
                time.sleep(1)

    def start_schedule(self):
        """Inicia o monitoramento do agendamento"""
        if not self.scheduled_thread or not self.scheduled_thread.is_alive():
            self.should_stop = False
            self.scheduled_thread = threading.Thread(target=self.check_schedule)
            self.scheduled_thread.daemon = True
            self.scheduled_thread.start()
            self.player.status_label.configure(text="Status: Agendamento ativado")
            print("Sistema de agendamento iniciado")

    def get_next_stream_time(self):
        """Calcula o próximo horário de reprodução"""
        try:
            now = datetime.now()
            start_time = dt_time.fromisoformat(self.player.start_time.get())
            start_datetime = datetime.combine(now.date(), start_time)

            if start_datetime < now:
                start_datetime = datetime.combine(now.date() + timedelta(days=1), start_time)

            return start_datetime
        except ValueError:
            return None

    def update_countdown(self):
        """Atualiza o contador regressivo"""
        try:
            if self.is_playing:
                countdown_text = "Reproduzindo..."
                color = "#28a745"
                text_color = "white"
            else:
                next_stream = self.get_next_stream_time()
                if next_stream:
                    time_diff = next_stream - datetime.now()
                    if time_diff.total_seconds() > 0:
                        hours = int(time_diff.total_seconds() // 3600)
                        minutes = int((time_diff.total_seconds() % 3600) // 60)
                        seconds = int(time_diff.total_seconds() % 60)
                        countdown_text = f"Próxima reprodução em: {hours:02d}:{minutes:02d}:{seconds:02d}"

                        if time_diff.total_seconds() <= 30:  # Últimos 30 segundos
                            color = "#dc3545" if self.blink_state else "#ffc107"
                            text_color = "white" if self.blink_state else "black"
                            self.blink_state = not self.blink_state
                        elif time_diff.total_seconds() <= 300:  # Últimos 5 minutos
                            color = "#ffc107"
                            text_color = "black"
                        else:
                            color = "#f8f9fa"
                            text_color = "black"
                    else:
                        countdown_text = "Iniciando a reprodução..."
                        color = "#ffc107"
                        text_color = "black"
                else:
                    countdown_text = "Horário inválido"
                    color = "#f8f9fa"
                    text_color = "black"

            self.player.countdown_frame.configure(fg_color=color)
            self.player.countdown_label.configure(text=countdown_text, text_color=text_color)
        except Exception as e:
            print(f"Erro ao atualizar countdown: {e}")
        finally:
            self.player.root.after(500, self.update_countdown)

    def load_config(self):
        """Carrega as configurações do arquivo"""
        if os.path.exists(self.player.config_file):
            try:
                with open(self.player.config_file, 'r') as f:
                    self.player.config = json.load(f)
                    self.player.url_entry.delete(0, "end")
                    self.player.url_entry.insert(0, self.player.config['stream_url'])
                    self.player.start_time.delete(0, "end")
                    self.player.start_time.insert(0, self.player.config['auto_start_time'])
                    self.player.stop_time.delete(0, "end")
                    self.player.stop_time.insert(0, self.player.config['auto_stop_time'])
            except json.JSONDecodeError:
                print("Erro ao ler arquivo de configuração, criando novo...")
                self.save_config()
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
        else:
            self.save_config()

    def save_config(self):
        """Salva as configurações no arquivo"""
        try:
            self.player.config['stream_url'] = self.player.url_entry.get()
            self.player.config['auto_start_time'] = self.player.start_time.get()
            self.player.config['auto_stop_time'] = self.player.stop_time.get()

            with open(self.player.config_file, 'w') as f:
                json.dump(self.player.config, f)
            self.player.status_label.configure(text="Status: Configurações salvas")
            print("Configurações salvas com sucesso")
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            self.player.status_label.configure(text=f"Erro ao salvar: {str(e)}")

    def update_clock(self):
        """Atualiza o relógio"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.player.clock_label.configure(text=current_time)
        except Exception as e:
            print(f"Erro ao atualizar relógio: {e}")
        finally:
            self.player.root.after(1000, self.update_clock)

    def on_closing(self):
        """Manipula o fechamento da aplicação"""
        print("Finalizando aplicação...")
        self.should_stop = True
        if self.scheduled_thread:
            self.scheduled_thread.join(timeout=1)
        if self.is_playing:
            self.stop()
        if self.instance:
            self.media_player.release()
            self.instance.release()
        self.player.root.destroy()
        print("Aplicação finalizada com sucesso")