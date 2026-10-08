from pathlib import Path

import pygame


class GestorAudio:
    """Gestiona la música de fondo y los efectos de sonido del juego."""

    CANALES_EFECTOS = 16

    def __init__(self) -> None:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()

        pygame.mixer.set_num_channels(self.CANALES_EFECTOS)
        self._efectos: dict[str, pygame.mixer.Sound] = {}

    def reproducir_musica(self, ruta_archivo: str | Path) -> None:
        """Carga una pista y la reproduce en bucle continuo como BGM."""
        pygame.mixer.music.load(str(ruta_archivo))
        pygame.mixer.music.play(loops=-1)

    def reproducir_efecto(self, ruta_archivo: str | Path) -> None:
        """Reproduce un SFX en un canal independiente, superpuesto a los demás."""
        ruta = str(ruta_archivo)
        efecto = self._efectos.get(ruta)
        if efecto is None:
            efecto = pygame.mixer.Sound(ruta)
            self._efectos[ruta] = efecto

        efecto.play()

    def detener_musica(self) -> None:
        """Detiene la pista de música de fondo actual."""
        pygame.mixer.music.stop()