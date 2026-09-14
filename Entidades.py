from abc import ABC, abstractmethod

import pygame


class ComponenteSalud:
    """Gestiona la vida y el daño recibido por una entidad."""

    def __init__(self, vida_inicial: int) -> None:
        if vida_inicial < 0:
            raise ValueError("La vida inicial no puede ser negativa")

        self.vida = vida_inicial

    def recibir_danio(self, cantidad: int) -> None:
        """Resta daño sin permitir que la vida sea inferior a cero."""
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo")

        self.vida = max(0, self.vida - cantidad)

    def esta_vivo(self) -> bool:
        """Indica si todavía queda vida."""
        return self.vida > 0


class EntidadBase(ABC):
    """Entidad con posición, hitbox y velocidad independientes del framerate."""

    TECLA_DERECHA = getattr(pygame, "K_RIGHT", 1073741903)
    TECLA_IZQUIERDA = getattr(pygame, "K_LEFT", 1073741904)
    TECLA_ABAJO = getattr(pygame, "K_DOWN", 1073741905)
    TECLA_ARRIBA = getattr(pygame, "K_UP", 1073741906)

    def __init__(self, x: float, y: float, ancho: int, alto: int) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.g = 980.0
        self.velocidad_horizontal = 220.0
        self.velocidad_vertical = 220.0
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
        direccion_y = teclas[self.TECLA_ABAJO] - teclas[self.TECLA_ARRIBA]
        self.vy = direccion_y * self.velocidad_vertical

    @abstractmethod
    def actualizar(self, dt: float) -> None:
        """Aplica controles, gravedad y movimiento usando segundos transcurridos."""
        self.preparar_actualizacion(dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.sincronizar_hitbox()


class Eco(EntidadBase):
    """Entidad controlada por el jugador en el primer nivel."""

    VIDA_INICIAL = 100
    DURACION_ATAQUE = 0.18
    ANCHO_ATAQUE = 30

    def __init__(self, x: float, y: float, ancho: int, alto: int) -> None:
        super().__init__(x, y, ancho, alto)
        self.salud = ComponenteSalud(self.VIDA_INICIAL)
        self.hurtbox = self.hitbox.copy()
        self.attackbox: pygame.Rect | None = None
        self.direccion = 1
        self.tiempo_ataque = 0.0
        self.temporizador_invulnerable = 0.0

    def sincronizar_hitbox(self) -> None:
        super().sincronizar_hitbox()
        self.hurtbox.topleft = self.hitbox.topleft

    def preparar_actualizacion(self, dt: float) -> None:
        super().preparar_actualizacion(dt)
        if self.vx != 0:
            self.direccion = 1 if self.vx > 0 else -1

    def iniciar_agarre(self) -> None:
        """Activa un área de interacción delante de Eco durante un instante."""
        if self.attackbox is not None:
            return

        self.tiempo_ataque = self.DURACION_ATAQUE
        self.attackbox = pygame.Rect(
            self.hitbox.right if self.direccion > 0 else self.hitbox.left - self.ANCHO_ATAQUE,
            self.hitbox.top,
            self.ANCHO_ATAQUE,
            self.hitbox.height,
        )

    def actualizar_ataque(self, dt: float) -> None:
        """Mantiene o desactiva el área de interacción según el tiempo restante."""
        if self.attackbox is None:
            return

        self.tiempo_ataque -= dt
        if self.tiempo_ataque <= 0:
            self.attackbox = None

    def actualizar_temporizador_invulnerable(self, dt: float) -> None:
        """Reduce la ventana de inmunidad usando el tiempo real transcurrido."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        self.temporizador_invulnerable -= dt

    def actualizar(self, dt: float) -> None:
        EntidadBase.actualizar(self, dt)
        self.actualizar_ataque(dt)
        self.actualizar_temporizador_invulnerable(dt)


class Dron(EntidadBase):
    """Enemigo estático de prueba con un área de daño propia."""

    VIDA_INICIAL = 100

    def __init__(self, x: float, y: float, ancho: int, alto: int) -> None:
        super().__init__(x, y, ancho, alto)
        self.salud = ComponenteSalud(self.VIDA_INICIAL)
        self.hurtbox = self.hitbox.copy()

    def sincronizar_hitbox(self) -> None:
        super().sincronizar_hitbox()
        self.hurtbox.topleft = self.hitbox.topleft

    def actualizar(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")