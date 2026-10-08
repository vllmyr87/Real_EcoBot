from dataclasses import dataclass
from math import cos, pi, sin
from random import choice, randint, uniform

import pygame


@dataclass(slots=True)
class _Particula:
    """Estado reutilizable de una partícula del emisor."""

    x: float = 0.0
    y: float = 0.0
    velocidad_x: float = 0.0
    velocidad_y: float = 0.0
    tiempo_restante: float = 0.0
    duracion_total: float = 1.0
    radio: int = 3
    color: tuple[int, int, int] = (255, 255, 255)

    @property
    def alpha(self) -> int:
        """Calcula la transparencia según la proporción de vida restante."""
        proporcion = self.tiempo_restante / self.duracion_total
        return max(0, min(255, round(proporcion * 255)))


class EmisorParticulas:
    """Emisor de explosiones con un pool fijo de objetos reutilizables."""

    MAX_PARTICULAS = 100
    PARTICULAS_POR_EXPLOSION = 15
    COLORES = (
        (255, 218, 86),
        (245, 112, 145),
        (112, 190, 92),
        (245, 239, 205),
    )
    GRAVEDAD = 180.0

    def __init__(self) -> None:
        self._inactivas = [_Particula() for _ in range(self.MAX_PARTICULAS)]
        self._activas: list[_Particula] = []
        self._capa: pygame.Surface | None = None

    @property
    def cantidad_activas(self) -> int:
        """Cantidad de partículas que se están actualizando y dibujando."""
        return len(self._activas)

    @property
    def cantidad_inactivas(self) -> int:
        """Cantidad de objetos disponibles para reutilizar en el pool."""
        return len(self._inactivas)

    def emitir(
        self,
        centro: tuple[int, int],
        cantidad: int = PARTICULAS_POR_EXPLOSION,
    ) -> int:
        """Activa partículas disponibles alrededor del centro recibido."""
        if cantidad < 0:
            raise ValueError("La cantidad de partículas no puede ser negativa")

        emitidas = min(cantidad, len(self._inactivas))
        for _ in range(emitidas):
            particula = self._inactivas.pop()
            angulo = uniform(0.0, 2 * pi)
            velocidad = uniform(65.0, 190.0)
            particula.x = float(centro[0])
            particula.y = float(centro[1])
            particula.velocidad_x = cos(angulo) * velocidad
            particula.velocidad_y = sin(angulo) * velocidad
            particula.duracion_total = uniform(0.65, 1.1)
            particula.tiempo_restante = particula.duracion_total
            particula.radio = randint(3, 5)
            particula.color = choice(self.COLORES)
            self._activas.append(particula)

        return emitidas

    def actualizar(self, dt: float) -> None:
        """Avanza movimiento y vida, devolviendo al pool las partículas vencidas."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        for particula in self._activas.copy():
            particula.tiempo_restante -= dt
            if particula.tiempo_restante <= 0:
                self._activas.remove(particula)
                self._reiniciar(particula)
                self._inactivas.append(particula)
                continue

            particula.x += particula.velocidad_x * dt
            particula.y += particula.velocidad_y * dt
            particula.velocidad_y += self.GRAVEDAD * dt

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja las partículas con alfa por píxel sobre una capa transparente."""
        if not self._activas:
            return

        if self._capa is None or self._capa.get_size() != pantalla.get_size():
            self._capa = pygame.Surface(pantalla.get_size()).convert_alpha()

        self._capa.fill((0, 0, 0, 0))
        for particula in self._activas:
            pygame.draw.circle(
                self._capa,
                (*particula.color, particula.alpha),
                (round(particula.x), round(particula.y)),
                particula.radio,
            )

        pantalla.blit(self._capa, (0, 0))

    @staticmethod
    def _reiniciar(particula: _Particula) -> None:
        """Limpia el estado antes de devolver el objeto al pool inactivo."""
        particula.x = 0.0
        particula.y = 0.0
        particula.velocidad_x = 0.0
        particula.velocidad_y = 0.0
        particula.tiempo_restante = 0.0
        particula.duracion_total = 1.0
        particula.radio = 3
        particula.color = (255, 255, 255)