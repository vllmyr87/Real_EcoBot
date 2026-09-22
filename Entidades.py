from abc import ABC, abstractmethod
from math import hypot

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


class Enemigo(Dron):
    """Enemigo con una máquina de estados finitos para su comportamiento."""

    ESTADO_PATRULLA = "Patrulla"
    ESTADO_PERSECUCION = "Persecución"
    ESTADO_ATAQUE = "Ataque"
    DISTANCIA_ALERTA = 300.0
    DISTANCIA_ATAQUE = 50.0
    DURACION_ATAQUE = 0.18
    ANCHO_ATAQUE = 30
    COOLDOWN_ATAQUE = 2.0

    def __init__(
        self,
        x: float,
        y: float,
        ancho: int,
        alto: int,
        objetivo: EntidadBase | None = None,
    ) -> None:
        super().__init__(x, y, ancho, alto)
        self.estado_actual = self.ESTADO_PATRULLA
        self.objetivo = objetivo
        self.direccion = 1
        self.velocidad_patrulla = 60.0
        self.velocidad_persecucion = 110.0
        self.limites_pantalla: tuple[int, int] | None = None
        self.attackbox: pygame.Rect | None = None
        self.tiempo_ataque = 0.0
        self.cooldown_ataque = 0.0

        # Cada estado conoce únicamente su comportamiento; actualizar solo lo despacha.
        self.comportamientos = {
            self.ESTADO_PATRULLA: self.actualizar_patrulla,
            self.ESTADO_PERSECUCION: self.actualizar_persecucion,
            self.ESTADO_ATAQUE: self.actualizar_ataque,
        }

    def cambiar_estado(self, nuevo_estado: str) -> None:
        """Cambia de estado solo si existe un comportamiento registrado."""
        if nuevo_estado not in self.comportamientos:
            raise ValueError(f"Estado de enemigo no válido: {nuevo_estado}")

        self.estado_actual = nuevo_estado

    def calcular_distancia_a(self, entidad: EntidadBase) -> float:
        """Calcula la distancia entre los centros de dos hitboxes."""
        diferencia_x = entidad.hitbox.centerx - self.hitbox.centerx
        diferencia_y = entidad.hitbox.centery - self.hitbox.centery
        return hypot(diferencia_x, diferencia_y)

    def establecer_objetivo(self, objetivo: EntidadBase) -> None:
        """Asigna la entidad que el enemigo debe vigilar y perseguir."""
        self.objetivo = objetivo

    def establecer_limites_pantalla(self, ancho: int, alto: int) -> None:
        """Define el área jugable donde el enemigo puede desplazarse."""
        if ancho <= 0 or alto <= 0:
            raise ValueError("Las dimensiones de la pantalla deben ser positivas")

        self.limites_pantalla = (ancho, alto)

    def limitar_a_pantalla(self) -> None:
        """Mantiene el hitbox dentro de la pantalla y corrige su dirección."""
        if self.limites_pantalla is None:
            return

        ancho, alto = self.limites_pantalla
        limite_x = max(0, ancho - self.hitbox.width)
        limite_y = max(0, alto - self.hitbox.height)
        llego_borde_izquierdo = self.x <= 0
        llego_borde_derecho = self.x >= limite_x

        self.x = max(0, min(self.x, limite_x))
        self.y = max(0, min(self.y, limite_y))
        self.sincronizar_hitbox()

        if llego_borde_izquierdo or llego_borde_derecho:
            self.direccion *= -1

    def actualizar_patrulla(self, dt: float) -> None:
        """Patrulla y activa la persecución cuando Eco entra en rango de alerta."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        if (
            self.objetivo is not None
            and self.calcular_distancia_a(self.objetivo) <= self.DISTANCIA_ALERTA
        ):
            self.cambiar_estado(self.ESTADO_PERSECUCION)
            return

        self.vx = self.direccion * self.velocidad_patrulla
        self.x += self.vx * dt
        self.sincronizar_hitbox()
        self.limitar_a_pantalla()

    def actualizar_persecucion(self, dt: float) -> None:
        """Persigue al objetivo y vuelve a patrulla cuando sale del rango de alerta."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        if self.objetivo is None:
            self.cambiar_estado(self.ESTADO_PATRULLA)
            return

        distancia = self.calcular_distancia_a(self.objetivo)
        if distancia > self.DISTANCIA_ALERTA:
            # Al escapar, la nueva patrulla debe alejarse del jugador para no
            # reactivar la alerta inmediatamente en el siguiente frame.
            self.direccion = (
                1
                if self.hitbox.centerx >= self.objetivo.hitbox.centerx
                else -1
            )
            self.cambiar_estado(self.ESTADO_PATRULLA)
            return

        if distancia <= self.DISTANCIA_ATAQUE and self.cooldown_ataque <= 0:
            self.cambiar_estado(self.ESTADO_ATAQUE)
            return

        diferencia_x = self.objetivo.hitbox.centerx - self.hitbox.centerx
        diferencia_y = self.objetivo.hitbox.centery - self.hitbox.centery
        self.vx = diferencia_x / distancia * self.velocidad_persecucion if distancia else 0.0
        self.vy = diferencia_y / distancia * self.velocidad_persecucion if distancia else 0.0
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.direccion = 1 if self.vx >= 0 else -1
        self.sincronizar_hitbox()
        self.limitar_a_pantalla()

    def actualizar_ataque(self, dt: float) -> None:
        """Activa el área de ataque y la retira al terminar su breve duración."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        self.vx = 0.0
        self.vy = 0.0

        if self.attackbox is None:
            self.tiempo_ataque = self.DURACION_ATAQUE
            self.cooldown_ataque = self.COOLDOWN_ATAQUE
            self.attackbox = pygame.Rect(
                self.hitbox.right
                if self.direccion > 0
                else self.hitbox.left - self.ANCHO_ATAQUE,
                self.hitbox.top,
                self.ANCHO_ATAQUE,
                self.hitbox.height,
            )

        self.tiempo_ataque -= dt
        if self.tiempo_ataque <= 0:
            self.attackbox = None
            self.cambiar_estado(self.ESTADO_PERSECUCION)

    def actualizar(self, dt: float) -> None:
        """Ejecuta exclusivamente el comportamiento asociado al estado actual."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        self.cooldown_ataque = max(0.0, self.cooldown_ataque - dt)
        self.comportamientos[self.estado_actual](dt)