import pygame

import Configuracion_UI as config_ui


class Boton_UI:
    """Botón interactivo con detección de clic mediante límites AABB."""

    COLOR_NORMAL = config_ui.COLOR_BOTON_NORMAL
    COLOR_HOVER = config_ui.COLOR_BOTON_HOVER
    COLOR_BORDE = config_ui.COLOR_BORDE
    COLOR_TEXTO = config_ui.COLOR_TEXTO
    FACTOR_HOVER = config_ui.FACTOR_HOVER_BOTON

    def __init__(self, x: int, y: int, ancho: int, alto: int, texto: str) -> None:
        if ancho <= 0 or alto <= 0:
            raise ValueError("Las dimensiones del botón deben ser mayores que cero")

        self.rect = pygame.Rect(x, y, ancho, alto)
        self.rect_visual = self.rect.copy()
        self.texto = texto
        self.fuente = pygame.font.Font(
            config_ui.FUENTE_BASE,
            config_ui.TAMANO_FUENTE_BOTON,
        )
        self.mouse_sobre = False

    def actualizar(self, posicion_mouse: tuple[int, int]) -> None:
        """Actualiza el hover y amplía la representación sin cambiar el hitbox."""
        self.mouse_sobre = self.rect.collidepoint(posicion_mouse)
        if self.mouse_sobre:
            ancho_visual = round(self.rect.width * self.FACTOR_HOVER)
            alto_visual = round(self.rect.height * self.FACTOR_HOVER)
            self.rect_visual = pygame.Rect(0, 0, ancho_visual, alto_visual)
            self.rect_visual.center = self.rect.center
        else:
            self.rect_visual = self.rect.copy()

    def comprobar_clic(
        self,
        posicion_mouse: tuple[int, int],
        clic_izquierdo: bool,
    ) -> bool:
        """Devuelve True si hubo clic izquierdo dentro del rectángulo."""
        return clic_izquierdo and self.rect.collidepoint(posicion_mouse)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el botón usando el estado hover actualizado."""
        color = self.COLOR_HOVER if self.mouse_sobre else self.COLOR_NORMAL
        pygame.draw.rect(
            pantalla,
            color,
            self.rect_visual,
            border_radius=config_ui.RADIO_BORDE_BOTON,
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_BORDE,
            self.rect_visual,
            width=2,
            border_radius=config_ui.RADIO_BORDE_BOTON,
        )
        superficie_texto = self.fuente.render(self.texto, True, self.COLOR_TEXTO)
        x_texto = (
            self.rect_visual.x
            + self.rect_visual.width / 2
            - superficie_texto.get_width() / 2
        )
        y_texto = (
            self.rect_visual.y
            + self.rect_visual.height / 2
            - superficie_texto.get_height() / 2
        )
        pantalla.blit(superficie_texto, (round(x_texto), round(y_texto)))


class Gestor_UI:
    """Dibuja la interfaz de juego superpuesta a la escena activa."""

    ANCHO_BARRA = config_ui.ANCHO_BARRA_SALUD
    ALTO_BARRA = config_ui.ALTO_BARRA_SALUD
    POSICION = config_ui.POSICION_BARRA_SALUD
    COLOR_PANEL = config_ui.COLOR_PANEL_SALUD
    COLOR_FONDO_BARRA = config_ui.COLOR_FONDO_BARRA_SALUD
    COLOR_BORDE = config_ui.COLOR_BORDE
    COLOR_SALUD_ALTA = config_ui.COLOR_SALUD_ALTA
    COLOR_SALUD_MEDIA = config_ui.COLOR_SALUD_MEDIA
    COLOR_SALUD_BAJA = config_ui.COLOR_SALUD_BAJA
    COLOR_TEXTO = config_ui.COLOR_TEXTO

    def __init__(self) -> None:
        self.fuente = pygame.font.Font(
            config_ui.FUENTE_BASE,
            config_ui.TAMANO_FUENTE_BARRA_SALUD,
        )

    def dibujar_barra_salud(
        self,
        pantalla: pygame.Surface,
        salud_actual: int,
        salud_maxima: int,
    ) -> None:
        """Dibuja la salud actual de Eco usando una proporción directa."""
        if salud_maxima <= 0:
            raise ValueError("La salud máxima debe ser mayor que cero")

        salud_visible = max(0, min(salud_actual, salud_maxima))
        ancho_interior = self.ANCHO_BARRA - 2
        ancho_salud = int((salud_visible / salud_maxima) * ancho_interior)
        x, y = self.POSICION
        desplazamiento_x, desplazamiento_y = config_ui.DESPLAZAMIENTO_BARRA_SALUD
        relleno_x, relleno_y = config_ui.DESPLAZAMIENTO_RELLENO_SALUD
        texto_x, texto_y = config_ui.DESPLAZAMIENTO_TEXTO_SALUD

        pygame.draw.rect(
            pantalla,
            self.COLOR_PANEL,
            (x, y, config_ui.ANCHO_PANEL_SALUD, config_ui.ALTO_PANEL_SALUD),
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_FONDO_BARRA,
            (
                x + desplazamiento_x,
                y + desplazamiento_y,
                self.ANCHO_BARRA,
                self.ALTO_BARRA,
            ),
        )

        if salud_visible > salud_maxima * 0.6:
            color_salud = self.COLOR_SALUD_ALTA
        elif salud_visible > salud_maxima * 0.3:
            color_salud = self.COLOR_SALUD_MEDIA
        else:
            color_salud = self.COLOR_SALUD_BAJA

        pygame.draw.rect(
            pantalla,
            color_salud,
            (
                x + desplazamiento_x + relleno_x,
                y + desplazamiento_y + relleno_y,
                ancho_salud,
                self.ALTO_BARRA - 2,
            ),
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_BORDE,
            (
                x + desplazamiento_x,
                y + desplazamiento_y,
                self.ANCHO_BARRA,
                self.ALTO_BARRA,
            ),
            1,
        )

        texto = self.fuente.render(
            f"ECO  {salud_visible} / {salud_maxima}",
            True,
            self.COLOR_TEXTO,
        )
        pantalla.blit(texto, (x + texto_x, y + texto_y))