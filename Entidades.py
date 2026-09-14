from abc import ABC, abstractmethod

import pygame


class EntidadBase(ABC):
    """Entidad con posición, hitbox y velocidad independientes del framerate."""

    TECLA_DERECHA = getattr(pygame, "K_RIGHT", 1073741903)
    TECLA_IZQUIERDA = getattr(pygame, "K_LEFT", 1073741904)

    def __init__(self, x: float, y: float, ancho: int, alto: int) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.g = 980.0
        self.velocidad_horizontal = 220.0
        self.hitbox = pygame.Rect(round(self.x), round(self.y), ancho, alto)

    def sincronizar_hitbox(self) -> None:
        """Mantiene el rectángulo alineado con las coordenadas de la entidad."""
        self.hitbox.topleft = (round(self.x), round(self.y))

    def preparar_actualizacion(self, dt: float) -> None:
        """Actualiza controles y velocidades antes de resolver el movimiento."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        teclas = pygame.key.get_pressed()
        direccion_x = teclas[self.TECLA_DERECHA] - teclas[self.TECLA_IZQUIERDA]
        self.vx = direccion_x * self.velocidad_horizontal
        self.vy += self.g * dt

    @abstractmethod
    def actualizar(self, dt: float) -> None:
        """Aplica controles, gravedad y movimiento usando segundos transcurridos."""
        self.preparar_actualizacion(dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.sincronizar_hitbox()


class Eco(EntidadBase):
    """Entidad controlada por el jugador en el primer nivel."""

    def actualizar(self, dt: float) -> None:
        EntidadBase.actualizar(self, dt)