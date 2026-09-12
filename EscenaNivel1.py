import pygame

from GestorEscenas import EscenaBase


class EscenaNivel1(EscenaBase):
    """Escenario base del primer nivel de EcoBot."""

    TECLA_DERECHA = getattr(pygame, "K_RIGHT", 1073741903)
    TECLA_IZQUIERDA = getattr(pygame, "K_LEFT", 1073741904)
    TECLA_ABAJO = getattr(pygame, "K_DOWN", 1073741905)
    TECLA_ARRIBA = getattr(pygame, "K_UP", 1073741906)

    COLOR_CIELO = (117, 190, 218)
    COLOR_SUELO = (72, 92, 64)
    COLOR_TERRENO = (104, 130, 82)
    COLOR_MONTANAS = (71, 104, 102)
    COLOR_SOL = (247, 214, 106)
    COLOR_ECO = (224, 238, 228)
    COLOR_ECO_DETALLE = (42, 74, 84)
    VELOCIDAD_ECO = 220.0

    def __init__(self) -> None:
        self.posicion_eco = pygame.Vector2(120, 450)
        self.tamano_eco = pygame.Vector2(34, 48)

    def mover_eco(self, dt: float) -> None:
        """Mueve a Eco usando segundos transcurridos y las teclas presionadas."""
        teclas = pygame.key.get_pressed()
        direccion = pygame.Vector2(
            teclas[self.TECLA_DERECHA] - teclas[self.TECLA_IZQUIERDA],
            teclas[self.TECLA_ABAJO] - teclas[self.TECLA_ARRIBA],
        )

        if direccion.length_squared() > 0:
            direccion = direccion.normalize()
            self.posicion_eco += direccion * self.VELOCIDAD_ECO * dt

    def limitar_posicion_eco(self, pantalla: pygame.Surface) -> None:
        """Mantiene a Eco dentro de los límites visibles del nivel."""
        ancho, alto = pantalla.get_size()
        margen_suelo = 70
        self.posicion_eco.x = max(
            0,
            min(self.posicion_eco.x, ancho - self.tamano_eco.x),
        )
        self.posicion_eco.y = max(
            0,
            min(
                self.posicion_eco.y,
                alto - margen_suelo - self.tamano_eco.y,
            ),
        )

    def actualizar(self, dt: float) -> None:
        """Actualiza el movimiento de Eco en el nivel."""
        self.mover_eco(dt)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el escenario provisional del primer nivel."""
        ancho, alto = pantalla.get_size()
        horizonte = alto * 2 // 3

        pantalla.fill(self.COLOR_CIELO)
        pygame.draw.circle(pantalla, self.COLOR_SOL, (ancho - 100, 90), 42)
        pygame.draw.polygon(
            pantalla,
            self.COLOR_MONTANAS,
            [
                (0, horizonte),
                (ancho // 5, horizonte - 150),
                (ancho // 3, horizonte - 55),
                (ancho // 2, horizonte - 190),
                (ancho * 3 // 5, horizonte - 80),
                (ancho * 4 // 5, horizonte - 165),
                (ancho, horizonte - 30),
                (ancho, horizonte),
            ],
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_TERRENO,
            (0, horizonte, ancho, alto - horizonte),
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_SUELO,
            (0, alto - 70, ancho, 70),
        )
        self.limitar_posicion_eco(pantalla)
        cuerpo_eco = pygame.Rect(
            round(self.posicion_eco.x),
            round(self.posicion_eco.y),
            round(self.tamano_eco.x),
            round(self.tamano_eco.y),
        )
        pygame.draw.rect(pantalla, self.COLOR_ECO, cuerpo_eco)
        pygame.draw.rect(pantalla, self.COLOR_ECO_DETALLE, cuerpo_eco, 3)
        pygame.draw.rect(
            pantalla,
            self.COLOR_ECO_DETALLE,
            (cuerpo_eco.x + 8, cuerpo_eco.y + 12, 6, 6),
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_ECO_DETALLE,
            (cuerpo_eco.right - 14, cuerpo_eco.y + 12, 6, 6),
        )