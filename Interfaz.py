import pygame


class Boton_UI:
    """Botón interactivo con detección de clic mediante límites AABB."""

    COLOR_NORMAL = (66, 145, 91)
    COLOR_HOVER = (82, 177, 103)
    COLOR_BORDE = (226, 232, 212)
    COLOR_TEXTO = (245, 245, 230)
    FACTOR_HOVER = 1.05

    def __init__(self, x: int, y: int, ancho: int, alto: int, texto: str) -> None:
        if ancho <= 0 or alto <= 0:
            raise ValueError("Las dimensiones del botón deben ser mayores que cero")

        self.rect = pygame.Rect(x, y, ancho, alto)
        self.rect_visual = self.rect.copy()
        self.texto = texto
        self.fuente = pygame.font.Font(None, 32)
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
        pygame.draw.rect(pantalla, color, self.rect_visual, border_radius=8)
        pygame.draw.rect(
            pantalla,
            self.COLOR_BORDE,
            self.rect_visual,
            width=2,
            border_radius=8,
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

    ANCHO_BARRA = 220
    ALTO_BARRA = 16
    POSICION = (20, 20)
    COLOR_PANEL = (30, 43, 39)
    COLOR_FONDO_BARRA = (67, 77, 69)
    COLOR_BORDE = (226, 232, 212)
    COLOR_SALUD_ALTA = (82, 177, 103)
    COLOR_SALUD_MEDIA = (226, 183, 75)
    COLOR_SALUD_BAJA = (210, 83, 70)
    COLOR_TEXTO = (245, 245, 230)

    def __init__(self) -> None:
        self.fuente = pygame.font.Font(None, 22)

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

        pygame.draw.rect(pantalla, self.COLOR_PANEL, (x, y, 252, 54))
        pygame.draw.rect(
            pantalla,
            self.COLOR_FONDO_BARRA,
            (x + 12, y + 27, self.ANCHO_BARRA, self.ALTO_BARRA),
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
            (x + 13, y + 28, ancho_salud, self.ALTO_BARRA - 2),
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_BORDE,
            (x + 12, y + 27, self.ANCHO_BARRA, self.ALTO_BARRA),
            1,
        )

        texto = self.fuente.render(
            f"ECO  {salud_visible} / {salud_maxima}",
            True,
            self.COLOR_TEXTO,
        )
        pantalla.blit(texto, (x + 12, y + 7))