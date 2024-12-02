from enum import Enum

class PlayerStatus(Enum):
    STOPPED = "Parado"
    PLAYING = "Reproduzindo"
    MANUAL_STOP = "Parado manualmente"
    ERROR = "Erro"

class Colors:
    PLAYING = "#28a745"
    STOPPED = "#f8f9fa"
    WARNING = "#ffc107"
    ERROR = "#dc3545"

class VolumeSettings:
    INITIAL_VOLUME = 100
    MIN_VOLUME = 0
    MAX_VOLUME = 100
    STEPS = 100