import pygame

from EscenaMenu import EscenaMenu
from EscenaNivel1 import EscenaNivel1
from GestorEscenas import GestorEscenas
from Interfaz import Gestor_UI


ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60
EVENTO_SALIR = getattr(pygame, "QUIT", 256)


def ejecutar_juego() -> None:
    """Inicializa Pygame y ejecuta el bucle principal de EcoBot."""
    getattr(pygame, "init")()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("EcoBot")
    reloj = pygame.time.Clock()
    gestor_ui = Gestor_UI()

    gestor_escenas = GestorEscenas()
    escena_menu = EscenaMenu(gestor_escenas)
    escena_nivel_1 = EscenaNivel1()
    gestor_escenas.registrar_escena("menu", escena_menu)
    gestor_escenas.registrar_escena("NIVEL_1", escena_nivel_1)
    gestor_escenas.cambiar_escena("menu")

    ejecutando = True
    while ejecutando:
        dt = reloj.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == EVENTO_SALIR:
                ejecutando = False
            else:
                gestor_escenas.procesar_evento(evento)

        gestor_escenas.actualizar(dt)
        gestor_escenas.dibujar(pantalla)
        if gestor_escenas.escena_actual is escena_nivel_1:
            gestor_ui.dibujar_barra_salud(
                pantalla,
                escena_nivel_1.eco.salud.vida,
                escena_nivel_1.eco.VIDA_INICIAL,
            )
        pygame.display.flip()

    getattr(pygame, "quit")()


if __name__ == "__main__":
    ejecutar_juego()

