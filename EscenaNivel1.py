import pygame

from Entidades import Eco
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
    COLOR_ARBOL = (92, 57, 33)
    COLOR_COPA = (45, 112, 60)

    def __init__(self) -> None:
        self.eco = Eco(120, 450, 34, 48)
        self.objetos_estaticos = [
            pygame.Rect(0, 530, 800, 70),
            pygame.Rect(370, 370, 60, 160),
        ]

    def mover_eco(self, dt: float) -> None:
        """Actualiza velocidades y resuelve el movimiento de Eco."""
        self.eco.preparar_actualizacion(dt)
        self.resolver_colisiones_aabb(dt)

    def resolver_colisiones_aabb(self, dt: float) -> None:
        """Resuelve colisiones primero en X y luego en Y para evitar bloqueos."""
        self.eco.x += self.eco.vx * dt
        self.eco.sincronizar_hitbox()

        for objeto in self.objetos_estaticos:
            if self.eco.hitbox.colliderect(objeto):
                if self.eco.vx > 0:
                    self.eco.x = objeto.left - self.eco.hitbox.width
                elif self.eco.vx < 0:
                    self.eco.x = objeto.right
                self.eco.vx = 0.0
                self.eco.sincronizar_hitbox()

        self.eco.y += self.eco.vy * dt
        self.eco.sincronizar_hitbox()

        for objeto in self.objetos_estaticos:
            if self.eco.hitbox.colliderect(objeto):
                if self.eco.vy > 0:
                    self.eco.y = objeto.top - self.eco.hitbox.height
                elif self.eco.vy < 0:
                    self.eco.y = objeto.bottom
                self.eco.vy = 0.0
                self.eco.sincronizar_hitbox()

    def limitar_posicion_eco(self, pantalla: pygame.Surface) -> None:
        """Mantiene a Eco dentro de los límites visibles del nivel."""
        ancho, alto = pantalla.get_size()
        self.eco.x = max(
            0,
            min(self.eco.x, ancho - self.eco.hitbox.width),
        )
        self.eco.y = max(
            0,
            min(
                self.eco.y,
                alto - self.eco.hitbox.height,
            ),
        )
        self.eco.sincronizar_hitbox()

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
        _, arbol = self.objetos_estaticos
        pygame.draw.rect(pantalla, self.COLOR_ARBOL, arbol)
        pygame.draw.circle(pantalla, self.COLOR_COPA, (arbol.centerx, arbol.top), 58)
        self.limitar_posicion_eco(pantalla)
        cuerpo_eco = self.eco.hitbox
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