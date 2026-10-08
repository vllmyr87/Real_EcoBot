import pygame

import Configuracion_UI as config_ui
from GestorEscenas import EscenaBase, GestorEscenas
from Interfaz import Boton_UI


class EscenaMenu(EscenaBase):
    """Escena inicial con opciones para comenzar la aventura."""

    EVENTO_TECLA = getattr(pygame, "KEYDOWN", 768)
    TECLA_ENTER = getattr(pygame, "K_RETURN", 13)
    EVENTO_MOUSE = getattr(pygame, "MOUSEBUTTONDOWN", 1025)
    BOTON_INICIAR = "NIVEL_1"
    COLOR_FONDO = config_ui.COLOR_FONDO_MENU
    COLOR_TITULO = config_ui.COLOR_TITULO_MENU
    COLOR_SUBTITULO = config_ui.COLOR_SUBTITULO_MENU

    def __init__(self, gestor_escenas: GestorEscenas) -> None:
        self.gestor_escenas = gestor_escenas
        self.fuente_titulo = pygame.font.Font(
            config_ui.FUENTE_BASE,
            config_ui.TAMANO_FUENTE_TITULO,
        )
        self.fuente_subtitulo = pygame.font.Font(
            config_ui.FUENTE_BASE,
            config_ui.TAMANO_FUENTE_SUBTITULO,
        )
        x, y = config_ui.POSICION_BOTON_INICIAR
        self.boton_iniciar = Boton_UI(
            x,
            y,
            config_ui.ANCHO_BOTON_INICIAR,
            config_ui.ALTO_BOTON_INICIAR,
            "COMENZAR",
        )

    def procesar_evento(self, evento: pygame.event.Event) -> None:
        """Inicia el primer nivel al pulsar ENTER o el botón con clic izquierdo."""
        if evento.type == self.EVENTO_TECLA and evento.key == self.TECLA_ENTER:
            self.gestor_escenas.cambiar_escena(self.BOTON_INICIAR)
        elif evento.type == self.EVENTO_MOUSE and evento.button == 1:
            if self.boton_iniciar.comprobar_clic(evento.pos, True):
                self.gestor_escenas.cambiar_escena(self.BOTON_INICIAR)

    def actualizar(self, dt: float) -> None:
        """Actualiza el estado hover del botón según la posición del mouse."""
        self.boton_iniciar.actualizar(pygame.mouse.get_pos())

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el título y el botón de inicio centrados en pantalla."""
        pantalla.fill(self.COLOR_FONDO)
        centro_x = pantalla.get_width() // 2

        titulo = self.fuente_titulo.render("ECOBOT", True, self.COLOR_TITULO)
        pantalla.blit(
            titulo,
            titulo.get_rect(center=(centro_x, config_ui.POSICION_TITULO_MENU_Y)),
        )

        subtitulo = self.fuente_subtitulo.render(
            "Una aventura para restaurar el equilibrio",
            True,
            self.COLOR_SUBTITULO,
        )
        pantalla.blit(
            subtitulo,
            subtitulo.get_rect(center=(centro_x, config_ui.POSICION_SUBTITULO_MENU_Y)),
        )

        self.boton_iniciar.dibujar(pantalla)