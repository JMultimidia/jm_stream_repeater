import customtkinter as ctk
from ..utils.constants import VolumeSettings

class VolumeView:
    def __init__(self, master_frame):
        self.frame = ctk.CTkFrame(master_frame)
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do controle de volume"""
        # Label de volume
        self.volume_label = ctk.CTkLabel(
            self.frame,
            text=f"Volume: {VolumeSettings.INITIAL_VOLUME}%"
        )
        self.volume_label.pack(side="left", padx=5)

        # Slider de volume
        self.volume_slider = ctk.CTkSlider(
            self.frame,
            from_=VolumeSettings.MIN_VOLUME,
            to=VolumeSettings.MAX_VOLUME,
            number_of_steps=VolumeSettings.STEPS,
            width=200
        )
        self.volume_slider.set(VolumeSettings.INITIAL_VOLUME)
        self.volume_slider.pack(side="left", padx=10)

    def get_frame(self):
        """Retorna o frame para ser posicionado no layout principal"""
        return self.frame

    def setup_callbacks(self, on_volume_change):
        """Configura o callback do slider"""
        self.volume_slider.configure(command=lambda v: on_volume_change(int(v)))

    def update_volume_display(self, volume):
        """Atualiza o display do volume"""
        self.volume_label.configure(text=f"Volume: {volume}%")
