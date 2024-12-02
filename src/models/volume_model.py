class VolumeModel:
    def __init__(self, player_model):
        from ..utils.constants import VolumeSettings
        self.player_model = player_model
        self.volume = VolumeSettings.INITIAL_VOLUME

    def set_volume(self, volume):
        """Define o volume do player"""
        try:
            from ..utils.constants import VolumeSettings
            # Garante que o volume está dentro dos limites
            volume = max(VolumeSettings.MIN_VOLUME, min(VolumeSettings.MAX_VOLUME, volume))
            self.volume = volume

            if self.player_model.media_player:
                self.player_model.media_player.audio_set_volume(volume)
            return True
        except Exception as e:
            print(f"Erro ao ajustar volume: {e}")
            return False

    def get_volume(self):
        """Retorna o volume atual"""
        try:
            if self.player_model.media_player:
                return self.player_model.media_player.audio_get_volume()
            return self.volume
        except:
            return self.volume