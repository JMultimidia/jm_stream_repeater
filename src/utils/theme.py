import customtkinter as ctk

class AppTheme:
    def __init__(self):
        self.colors = {
            'bg': "#0a3d62",
            'accent': "#222f3e",
            'text': "#FFFFFF",
            'success': "#28C840",
            'warning': "#FFB302",
            'error': "#FF3B30"
        }

    def setup(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def get_color(self, name):
        return self.colors.get(name)