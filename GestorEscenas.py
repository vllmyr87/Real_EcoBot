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

    def __init__(self) -> None:
        self.estados: dict[str, EscenaBase] = {}
        self.escena_actual: EscenaBase | None = None

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

    def procesar_evento(self, evento: pygame.event.Event) -> None:
        """Envía un evento a la escena activa."""
        if self.escena_actual is not None:
            self.escena_actual.procesar_evento(evento)

    def actualizar(self, dt: float) -> None:
        """Actualiza la escena activa si existe."""
        if self.escena_actual is not None:
            self.escena_actual.actualizar(dt)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena activa si existe."""
        if self.escena_actual is not None:
            self.escena_actual.dibujar(pantalla)