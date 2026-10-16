from pathlib import Path

import pygame


class GestorAudio:
    """Gestiona la música de fondo y los efectos de sonido del juego."""

    CANALES_EFECTOS = 16
    CANAL_MUSICA = 0
    VOLUMEN_MUSICA = 0.4
    VOLUMEN_EFECTOS = 0.75
    DURACION_FUNDIDO_MS = 900
    RUTA_AUDIO = Path(__file__).with_name("sound")
    RUTA_MUSICA_NIVEL_1 = RUTA_AUDIO / "musica_fondo_aventura_retro.wav"
    RUTAS_EFECTOS = (
        RUTA_AUDIO / "sonido_reciclaje_flor_exito.wav",
        RUTA_AUDIO / "sonido_dron_destruyendose.wav",
    )

    def __init__(self) -> None:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()

        pygame.mixer.set_num_channels(self.CANALES_EFECTOS + 1)
        pygame.mixer.set_reserved(1)
        self._canal_musica = pygame.mixer.Channel(self.CANAL_MUSICA)
        rutas_recursos = (self.RUTA_MUSICA_NIVEL_1, *self.RUTAS_EFECTOS)
        self._recursos: dict[str, pygame.mixer.Sound] = {
            str(ruta): pygame.mixer.Sound(str(ruta)) for ruta in rutas_recursos
        }
        self._musica_actual: str | None = None

        self._recursos[str(self.RUTA_MUSICA_NIVEL_1)].set_volume(
            self.VOLUMEN_MUSICA
        )
        for ruta in self.RUTAS_EFECTOS:
            self._recursos[str(ruta)].set_volume(self.VOLUMEN_EFECTOS)

    def reproducir_musica(self, ruta_archivo: str | Path) -> None:
        """Reproduce en bucle una pista precargada en su canal dedicado."""
        ruta = str(ruta_archivo)
        musica = self._recursos.get(ruta)
        if musica is None:
            musica = pygame.mixer.Sound(ruta)
            musica.set_volume(self.VOLUMEN_MUSICA)
            self._recursos[ruta] = musica

        if self._musica_actual == ruta and self._canal_musica.get_busy():
            return

        self._canal_musica.play(
            musica,
            loops=-1,
            fade_ms=self.DURACION_FUNDIDO_MS,
        )
        self._musica_actual = ruta

    def reproducir_efecto(self, ruta_archivo: str | Path) -> None:
        """Reproduce un SFX en un canal independiente, superpuesto a los demás."""
        ruta = str(ruta_archivo)
        efecto = self._recursos.get(ruta)
        if efecto is None:
            efecto = pygame.mixer.Sound(ruta)
            efecto.set_volume(self.VOLUMEN_EFECTOS)
            self._recursos[ruta] = efecto

        efecto.play()

    def detener_musica(self) -> None:
        """Reduce gradualmente la música al salir del nivel."""
        if self._musica_actual is not None:
            self._canal_musica.fadeout(self.DURACION_FUNDIDO_MS)
            self._musica_actual = None