import vlc
import json
import os
from datetime import datetime, time as dt_time, timedelta
import threading

class PlayerModel:
    def __init__(self):
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            'settings.json'
        )
        self.config = self._get_default_config()
        self._setup_player_state()
        self._initialize_vlc()
        self._load_config()  # Renomeado para _load_config para manter o padrão

    def _get_default_config(self):
        """Retorna as configurações padrão"""
        return {
            'stream_url': 'http://exemplo.com/stream',
            'auto_start_time': '19:00:00',
            'auto_stop_time': '20:00:00'
        }

    def _setup_player_state(self):
        """Inicializa o estado do player"""
        self.is_playing = False
        self.manual_play = False
        self.manual_stop = False
        self.scheduled_thread = None
        self.should_stop = False
        self.blink_state = False
        self.user_interrupted = False

    def _initialize_vlc(self):
        """Inicializa o player VLC com configurações otimizadas"""
        try:
            self.instance = vlc.Instance('--no-xlib --quiet --aout=pulse')
            self.media_player = self.instance.media_player_new()
            print("VLC inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar VLC: {e}")
            self.instance = None
            self.media_player = None

    def _load_config(self):
        """Carrega as configurações do arquivo"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                return self.config
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                return self._get_default_config()
        return self._get_default_config()

    def get_config(self):
        """Retorna as configurações atuais"""
        return self.config

    def save_config(self, config_data):
        """Salva as configurações no arquivo"""
        try:
            self.config.update(config_data)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False

    def ensure_vlc_initialized(self):
        """Garante que o VLC está inicializado"""
        if self.instance is None or self.media_player is None:
            self._initialize_vlc()
            if self.instance is None or self.media_player is None:
                raise Exception("Não foi possível inicializar o VLC")

    def start_playback(self, url, manual=False):
        """Inicia a reprodução do stream"""
        try:
            self.ensure_vlc_initialized()

            if not url:
                raise ValueError("URL do stream não pode estar vazia")

            media = self.instance.media_new(url)
            media.add_option('--network-caching=1000')

            if not media:
                raise ValueError("Não foi possível criar mídia a partir da URL")

            self.media_player.set_media(media)
            self.media_player.video_set_scale(0)
            result = self.media_player.play()

            if result == 0:
                self.is_playing = True
                self.manual_play = manual
                if manual:
                    self.user_interrupted = False
                return True
            else:
                raise Exception(f"Erro ao iniciar reprodução: código {result}")

        except Exception as e:
            print(f"Erro ao iniciar reprodução: {e}")
            self.is_playing = False
            self.manual_play = False
            self._initialize_vlc()
            return False

    def stop_playback(self, manual=False):
        """Para a reprodução"""
        try:
            if self.is_playing and self.media_player:
                self.media_player.stop()
                self.is_playing = False
                self.manual_play = False
                if manual:
                    self.user_interrupted = True
                    print("Reprodução interrompida pelo usuário")
                return True
            return False
        except Exception as e:
            print(f"Erro ao parar: {e}")
            self.is_playing = False
            self.manual_play = False
            self._initialize_vlc()
            return False

    def get_next_stream_time(self):
        """Calcula o próximo horário de reprodução"""
        try:
            now = datetime.now()
            start_time = dt_time.fromisoformat(self.config['auto_start_time'])
            start_datetime = datetime.combine(now.date(), start_time)

            if start_datetime < now:
                start_datetime = datetime.combine(now.date() + timedelta(days=1), start_time)

            return start_datetime
        except ValueError:
            return None

    def check_schedule(self):
        """Verifica se está no horário agendado para reprodução"""
        try:
            current_time = datetime.now()
            start_time = dt_time.fromisoformat(self.config['auto_start_time'])
            stop_time = dt_time.fromisoformat(self.config['auto_stop_time'])

            current_datetime = current_time
            start_datetime = datetime.combine(current_time.date(), start_time)
            stop_datetime = datetime.combine(current_time.date(), stop_time)

            if stop_time < start_time:
                if current_datetime.time() < start_time:
                    stop_datetime = datetime.combine(current_time.date(), stop_time)
                else:
                    stop_datetime = datetime.combine(current_time.date() + timedelta(days=1), stop_time)

            within_schedule = (start_datetime <= current_datetime < stop_datetime)
            schedule_ended = (current_datetime >= stop_datetime)

            if schedule_ended:
                self.user_interrupted = False

            return {
                'should_be_playing': within_schedule and not self.user_interrupted,
                'schedule_ended': schedule_ended
            }

        except ValueError as e:
            print(f"Erro no formato do horário: {e}")
            return None

    def cleanup(self):
        """Limpa recursos ao fechar a aplicação"""
        self.should_stop = True
        if self.scheduled_thread:
            self.scheduled_thread.join(timeout=1)
        if self.is_playing:
            self.stop_playback()
        if self.instance:
            self.media_player.release()
            self.instance.release()