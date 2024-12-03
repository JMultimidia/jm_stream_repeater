# src/views/audio_config_view.py
import customtkinter as ctk


class AudioConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent, devices, current_device, on_save):
        super().__init__(parent)
        self.title("Configuração de Áudio")
        self.geometry("400x300")

        # Callbacks
        self.on_save = on_save

        # Layout
        self.grid_columnconfigure(0, weight=1)

        # Label
        ctk.CTkLabel(
            self,
            text="Selecione o Dispositivo de Saída:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, pady=10, padx=10)

        # Lista de dispositivos
        self.device_var = ctk.StringVar(value=current_device)
        self.device_list = ctk.CTkOptionMenu(
            self,
            values=[d['name'] for d in devices],
            variable=self.device_var
        )
        self.device_list.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        # Guardar referência dos devices
        self.devices = {d['name']: d['id'] for d in devices}

        # Botão Salvar
        ctk.CTkButton(
            self,
            text="Salvar",
            command=self._handle_save
        ).grid(row=2, column=0, pady=20)

    def _handle_save(self):
        selected_name = self.device_var.get()
        device_id = self.devices.get(selected_name, '')
        self.on_save(device_id)
        self.destroy()