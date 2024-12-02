class VolumeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.setup_controller()

    def setup_controller(self):
        """Configura o controller"""
        self.view.setup_callbacks(self.handle_volume_change)

    def handle_volume_change(self, volume):
        """Manipula mudanças no volume"""
        if self.model.set_volume(volume):
            self.view.update_volume_display(volume)