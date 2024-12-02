import customtkinter as ctk
from ..controllers.player_controller import PlayerController
from ..views.player_view import PlayerView
from ..models.player_model import PlayerModel


class Application:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup()

    def setup(self):
        # Configuração do tema
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Inicialização MVC
        self.model = PlayerModel()
        self.view = PlayerView(self.root)
        self.controller = PlayerController(self.model, self.view)

        # Inicialização do controle de volume
        from ..models.volume_model import VolumeModel
        from ..controllers.volume_controller import VolumeController

        self.volume_model = VolumeModel(self.model)
        self.volume_controller = VolumeController(
            self.volume_model,
            self.view.volume_view
        )

        # Configuração da janela
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)

    def run(self):
        self.root.mainloop()