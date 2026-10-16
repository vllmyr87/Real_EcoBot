import pygame

from EscenaMenu import EscenaMenu
from EscenaNivel1 import EscenaNivel1
from GestorEscenas import GestorEscenas
from Interfaz import Gestor_UI
from Particulas import EmisorParticulas


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
    emisor_particulas = EmisorParticulas()

    gestor_escenas = GestorEscenas()
    escena_menu = EscenaMenu(gestor_escenas)
    escena_nivel_1 = EscenaNivel1()
    gestor_escenas.registrar_escena("menu", escena_menu)
    gestor_escenas.registrar_escena("NIVEL_1", escena_nivel_1)
    gestor_escenas.cambiar_escena("menu")

    tiempo_hitstop = 0.0
    ejecutando = True
    while ejecutando:
        dt = reloj.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == EVENTO_SALIR:
                ejecutando = False
            else:
                gestor_escenas.procesar_evento(evento)

        if gestor_escenas.escena_actual is escena_nivel_1:
            escena_nivel_1.gestor_audio.reproducir_musica(
                escena_nivel_1.RUTA_MUSICA
            )
        else:
            escena_nivel_1.gestor_audio.detener_musica()

        hitstop_activo = tiempo_hitstop > 0
        if hitstop_activo:
            tiempo_hitstop = max(0.0, tiempo_hitstop - dt)
        gestor_escenas.actualizar(dt, actualizar_escena=not hitstop_activo)

        if (
            gestor_escenas.escena_actual is escena_nivel_1
            and escena_nivel_1.consumir_muerte_pendiente()
        ):
            tiempo_hitstop = 0.1
            hitstop_activo = True
            gestor_escenas.iniciar_transicion("menu")

        if gestor_escenas.escena_actual is escena_nivel_1:
            for centro in escena_nivel_1.consumir_explosiones_pendientes():
                emisor_particulas.emitir(
                    centro,
                    EmisorParticulas.PARTICULAS_POR_EXPLOSION,
                )
        if not hitstop_activo:
            emisor_particulas.actualizar(dt)
        gestor_escenas.dibujar(pantalla)
        emisor_particulas.dibujar(pantalla)
        if gestor_escenas.escena_actual is escena_nivel_1:
            gestor_ui.dibujar_barra_salud(
                pantalla,
                escena_nivel_1.eco.salud.vida,
                escena_nivel_1.eco.VIDA_INICIAL,
            )
        gestor_escenas.dibujar_transicion(pantalla)
        pygame.display.flip()

    getattr(pygame, "quit")()


if __name__ == "__main__":
    ejecutar_juego()
