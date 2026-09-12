import pygame

from GestorEscenas import EscenaBase, GestorEscenas


class EscenaMenu(EscenaBase):
    """Escena inicial con la indicación para comenzar la aventura."""

    EVENTO_TECLA = getattr(pygame, "KEYDOWN", 768)
    TECLA_ENTER = getattr(pygame, "K_RETURN", 13)

    def __init__(self, gestor_escenas: GestorEscenas) -> None:
        self.gestor_escenas = gestor_escenas
        self.fuente = pygame.font.Font(None, 36)
        self.texto = self.fuente.render(
            "Presiona ENTER para iniciar la aventura",
            True,
            (255, 255, 255),
        )

    def procesar_evento(self, evento: pygame.event.Event) -> None:
        """Cambia al primer nivel cuando se presiona ENTER."""
        if evento.type == self.EVENTO_TECLA and evento.key == self.TECLA_ENTER:
            self.gestor_escenas.cambiar_escena("nivel_1")

    def actualizar(self, dt: float) -> None:
        """Reserva el punto de actualización de la lógica del menú."""

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el texto del menú centrado en la pantalla."""
        posicion = self.texto.get_rect(center=pantalla.get_rect().center)
        pantalla.blit(self.texto, posicion)