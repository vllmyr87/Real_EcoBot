from abc import ABC, abstractmethod

import pygame


class EscenaBase(ABC):
    """Contrato común para todas las escenas del juego."""

    def procesar_evento(self, evento: pygame.event.Event) -> None:
        """Permite que una escena responda a eventos de Pygame."""

    @abstractmethod
    def actualizar(self, dt: float) -> None:
        """Actualiza la lógica de la escena."""
        raise NotImplementedError

    @abstractmethod
    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena en la pantalla recibida."""
        raise NotImplementedError


class GestorEscenas:
    """Registra, activa y ejecuta la escena actualmente seleccionada."""

    OPACIDAD_MAXIMA = 255.0
    VELOCIDAD_FUNDIDO = 255.0

    def __init__(self) -> None:
        self.estados: dict[str, EscenaBase] = {}
        self.escena_actual: EscenaBase | None = None
        self.opacidad_transicion = 0.0
        self._fase_transicion: str | None = None
        self._destino_transicion: str | None = None
        self._capa_transicion: pygame.Surface | None = None

    def registrar_escena(self, nombre: str, escena: EscenaBase) -> None:
        """Agrega una escena al diccionario de estados disponibles."""
        if nombre in self.estados:
            raise ValueError(f"Ya existe una escena registrada con el nombre: {nombre}")

        self.estados[nombre] = escena

    def cambiar_escena(self, nombre: str) -> None:
        """Activa una escena previamente registrada."""
        if nombre not in self.estados:
            raise KeyError(f"No existe una escena registrada con el nombre: {nombre}")

        self.escena_actual = self.estados[nombre]

    def iniciar_transicion(self, nombre_destino: str) -> None:
        """Inicia un fundido a negro antes de activar la escena de destino."""
        if nombre_destino not in self.estados:
            raise KeyError(f"No existe una escena registrada con el nombre: {nombre_destino}")
        if self._fase_transicion is not None:
            return

        self._destino_transicion = nombre_destino
        self._fase_transicion = "salida"
        self.opacidad_transicion = 0.0

    def procesar_evento(self, evento: pygame.event.Event) -> None:
        """Envía un evento a la escena activa."""
        if self.escena_actual is not None:
            self.escena_actual.procesar_evento(evento)

    def actualizar(self, dt: float, actualizar_escena: bool = True) -> None:
        """Avanza el fundido y actualiza la escena si no está congelada."""
        if dt < 0:
            raise ValueError("Delta Time no puede ser negativo")

        if self._fase_transicion == "salida":
            self.opacidad_transicion = min(
                self.OPACIDAD_MAXIMA,
                self.opacidad_transicion + self.VELOCIDAD_FUNDIDO * dt,
            )
            if self.opacidad_transicion >= self.OPACIDAD_MAXIMA:
                if self._destino_transicion is not None:
                    self.cambiar_escena(self._destino_transicion)
                self._fase_transicion = "entrada"
        elif self._fase_transicion == "entrada":
            self.opacidad_transicion = max(
                0.0,
                self.opacidad_transicion - self.VELOCIDAD_FUNDIDO * dt,
            )
            if self.opacidad_transicion <= 0:
                self._fase_transicion = None
                self._destino_transicion = None

        if (
            actualizar_escena
            and self._fase_transicion != "salida"
            and self.escena_actual is not None
        ):
            self.escena_actual.actualizar(dt)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena activa si existe."""
        if self.escena_actual is not None:
            self.escena_actual.dibujar(pantalla)

    def dibujar_transicion(self, pantalla: pygame.Surface) -> None:
        """Superpone el rectángulo negro con la opacidad actual del fundido."""
        if self.opacidad_transicion <= 0:
            return

        if (
            self._capa_transicion is None
            or self._capa_transicion.get_size() != pantalla.get_size()
        ):
            self._capa_transicion = pygame.Surface(pantalla.get_size())
            self._capa_transicion.fill((0, 0, 0))

        self._capa_transicion.set_alpha(round(self.opacidad_transicion))
        pantalla.blit(self._capa_transicion, (0, 0))