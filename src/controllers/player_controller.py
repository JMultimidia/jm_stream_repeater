import threading
import time
from datetime import datetime


class PlayerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.setup_controller()

    def setup_controller(self):
        """Configura o controller e inicia os processos necessários"""
        # Configura callbacks da view
        self.view.setup_bindings(
            play_callback=self.handle_play,
            stop_callback=self.handle_stop,
            save_callback=self.handle_save_config
        )

        # Inicializa a aplicação
        self.initialize_app()

    def initialize_app(self):
        """Inicializa a aplicação carregando configurações e iniciando processos"""
        # Carrega configurações
        config = self.model.get_config()
        if config:
            self.view.update_config_fields(config)

        # Inicia processos
        self.start_schedule_check()
        self.view.start_clock_update()
        self.view.start_countdown_update(self.get_countdown_info)

    def handle_play(self):
        """Manipula o evento de play"""
        if not self.model.is_playing:
            url = self.view.get_stream_url()
            if self.model.start_playback(url, manual=True):
                self.view.update_status("Reproduzindo (Manual)")
                self.view.update_player_state(is_playing=True)

    def handle_stop(self):
        """Manipula o evento de stop"""
        if self.model.stop_playback(manual=True):
            self.view.update_status("Parado manualmente")
            self.view.update_player_state(is_playing=False)

    def handle_save_config(self):
        """Manipula o salvamento de configurações"""
        config_data = self.view.get_config_data()
        if self.model.save_config(config_data):
            self.view.update_status("Configurações salvas")
        else:
            self.view.update_status("Erro ao salvar configurações")

    def start_schedule_check(self):
        """Inicia a verificação de agendamento em uma thread separada"""
        self.schedule_thread = threading.Thread(target=self._schedule_check_loop)
        self.schedule_thread.daemon = True
        self.schedule_thread.start()

    def _schedule_check_loop(self):
        """Loop de verificação do agendamento"""
        while not self.model.should_stop:
            try:
                schedule_status = self.model.check_schedule()

                if schedule_status:
                    if schedule_status[
                        'should_be_playing'] and not self.model.is_playing and not self.model.manual_stop:
                        # Inicia reprodução agendada
                        self.view.root.after(0, self._start_scheduled_playback)

                    elif schedule_status['schedule_ended'] and self.model.is_playing and not self.model.manual_play:
                        # Para reprodução agendada
                        self.view.root.after(0, self._stop_scheduled_playback)
                        self.model.manual_stop = False

            except Exception as e:
                print(f"Erro na verificação do agendamento: {e}")

            time.sleep(1)

    def _start_scheduled_playback(self):
        """Inicia reprodução agendada"""
        url = self.view.get_stream_url()
        if self.model.start_playback(url, manual=False):
            self.view.update_status("Reproduzindo (Agendado)")
            self.view.update_player_state(is_playing=True)

    def _stop_scheduled_playback(self):
        """Para reprodução agendada"""
        if self.model.stop_playback(manual=False):
            self.view.update_status("Parado (Agendado)")
            self.view.update_player_state(is_playing=False)

    def get_countdown_info(self):
        """Retorna informações para atualização do countdown"""
        try:
            if self.model.is_playing:
                return {
                    'text': "Reproduzindo...",
                    'color': "#28a745",
                    'text_color': "white"
                }

            next_stream = self.model.get_next_stream_time()
            if not next_stream:
                return {
                    'text': "Horário inválido",
                    'color': "#f8f9fa",
                    'text_color': "black"
                }

            time_diff = next_stream - datetime.now()
            if time_diff.total_seconds() <= 0:
                return {
                    'text': "Iniciando a reprodução...",
                    'color': "#ffc107",
                    'text_color': "black"
                }

            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            seconds = int(time_diff.total_seconds() % 60)
            countdown_text = f"Próxima reprodução em: {hours:02d}:{minutes:02d}:{seconds:02d}"

            if time_diff.total_seconds() <= 30:
                color = "#dc3545" if self.model.blink_state else "#ffc107"
                text_color = "white" if self.model.blink_state else "black"
                self.model.blink_state = not self.model.blink_state
            elif time_diff.total_seconds() <= 300:
                color = "#ffc107"
                text_color = "black"
            else:
                color = "#f8f9fa"
                text_color = "black"

            return {
                'text': countdown_text,
                'color': color,
                'text_color': text_color
            }

        except Exception as e:
            print(f"Erro ao calcular countdown: {e}")
            return {
                'text': "Erro ao calcular tempo",
                'color': "#f8f9fa",
                'text_color': "black"
            }

    def on_closing(self):
        """Manipula o fechamento da aplicação"""
        self.model.cleanup()
        self.view.root.destroy()