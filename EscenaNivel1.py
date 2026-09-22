import pygame

from Entidades import Eco, Enemigo
from GestorEscenas import EscenaBase


class EscenaNivel1(EscenaBase):
    """Nivel cenital y panorámico con movimiento libre en dos dimensiones."""

    TECLA_DERECHA = getattr(pygame, "K_RIGHT", 1073741903)
    TECLA_IZQUIERDA = getattr(pygame, "K_LEFT", 1073741904)
    TECLA_ABAJO = getattr(pygame, "K_DOWN", 1073741905)
    TECLA_ARRIBA = getattr(pygame, "K_UP", 1073741906)
    EVENTO_TECLA = getattr(pygame, "KEYDOWN", 768)
    TECLA_ESPACIO = getattr(pygame, "K_SPACE", 32)

    COLOR_FONDO = (155, 192, 133)
    COLOR_CAMINO = (186, 163, 113)
    COLOR_AGUA = (91, 169, 190)
    COLOR_ECO = (224, 238, 228)
    COLOR_ECO_DETALLE = (42, 74, 84)
    COLOR_ARBOL = (92, 57, 33)
    COLOR_COPA = (45, 112, 60)
    COLOR_DRON = (180, 72, 54)
    COLOR_DRON_COOLDOWN = (220, 145, 55)
    COLOR_DRON_DETALLE = (55, 35, 38)
    COLOR_ATAQUE = (246, 230, 109)
    COLOR_RESIDUO = (52, 48, 42)
    COLOR_PLANTA = (47, 145, 70)
    DANIO_DRON = 10
    RETROCESO_COLISION = 12

    def __init__(self) -> None:
        self.eco = Eco(100, 270, 34, 48)
        self.dron = Enemigo(660, 270, 52, 48, objetivo=self.eco)
        self.residuo_contaminante = pygame.Rect(390, 270, 26, 26)
        self.planta_crecida = False
        self.objetos_estaticos = [
            pygame.Rect(300, 150, 90, 100),
            pygame.Rect(300, 350, 90, 100),
            pygame.Rect(485, 170, 70, 90),
            pygame.Rect(485, 350, 70, 90),
        ]

    def mover_eco(self, dt: float) -> None:
        """Actualiza velocidades y resuelve el movimiento de Eco."""
        self.eco.preparar_actualizacion(dt)
        self.resolver_colisiones_aabb(dt)
        self.eco.actualizar_ataque(dt)
        self.eco.actualizar_temporizador_invulnerable(dt)
        self.resolver_colision_eco_dron()
        self.resolver_interaccion()

    def procesar_evento(self, evento: pygame.event.Event) -> None:
        """Inicia el agarre de Eco al recibir la pulsación de espacio."""
        if evento.type == self.EVENTO_TECLA and evento.key == self.TECLA_ESPACIO:
            self.eco.iniciar_agarre()

    def resolver_interaccion(self) -> None:
        """Resuelve el agarre del residuo y el ataque de Eco."""
        if (
            self.eco.attackbox is not None
            and not self.planta_crecida
            and self.eco.attackbox.colliderect(self.residuo_contaminante)
        ):
            self.planta_crecida = True

        if (
            self.eco.attackbox is not None
            and self.eco.attackbox.colliderect(self.dron.hurtbox)
        ):
            self.dron.salud.recibir_danio(25)

    def resolver_ataque_dron(self) -> None:
        """Aplica el daño del ataque del Dron cuando alcanza a Eco."""
        if (
            self.dron.attackbox is not None
            and self.dron.attackbox.colliderect(self.eco.hurtbox)
            and self.eco.temporizador_invulnerable <= 0
        ):
            self.eco.salud.recibir_danio(self.DANIO_DRON)
            self.eco.temporizador_invulnerable = 1.0

    def resolver_colision_eco_dron(self) -> None:
        """Aplica daño e invulnerabilidad al contacto AABB entre ambas entidades."""
        if not self.eco.hurtbox.colliderect(self.dron.hurtbox):
            return

        if self.eco.temporizador_invulnerable <= 0:
            self.eco.salud.recibir_danio(self.DANIO_DRON)
            self.eco.temporizador_invulnerable = 1.0

        desplazamiento = self.eco.hurtbox.clip(self.dron.hurtbox)
        if desplazamiento.width < desplazamiento.height:
            desplazamiento_x = (
                -self.RETROCESO_COLISION
                if self.eco.hurtbox.centerx < self.dron.hurtbox.centerx
                else self.RETROCESO_COLISION
            )
            self.eco.x += desplazamiento_x
        else:
            desplazamiento_y = (
                -self.RETROCESO_COLISION
                if self.eco.hurtbox.centery < self.dron.hurtbox.centery
                else self.RETROCESO_COLISION
            )
            self.eco.y += desplazamiento_y
        self.eco.sincronizar_hitbox()

    def resolver_colisiones_aabb(self, dt: float) -> None:
        """Resuelve movimiento cenital en X e Y para evitar bloqueos."""
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
        self.eco.y = max(0, min(self.eco.y, alto - self.eco.hitbox.height))
        self.eco.sincronizar_hitbox()

    def actualizar(self, dt: float) -> None:
        """Actualiza el movimiento de Eco en el nivel."""
        self.mover_eco(dt)
        pantalla = pygame.display.get_surface()
        if pantalla is not None:
            ancho, alto = pantalla.get_size()
            self.dron.establecer_limites_pantalla(ancho, alto)
        self.dron.actualizar(dt)
        self.resolver_ataque_dron()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el escenario provisional del primer nivel."""
        ancho, alto = pantalla.get_size()

        pantalla.fill(self.COLOR_FONDO)
        pygame.draw.rect(pantalla, self.COLOR_CAMINO, (0, 245, ancho, 70))
        pygame.draw.rect(pantalla, self.COLOR_CAMINO, (430, 0, 70, alto))
        pygame.draw.rect(pantalla, self.COLOR_AGUA, (0, 0, 175, 105))
        pygame.draw.rect(pantalla, self.COLOR_AGUA, (625, 495, 175, 105))
        for arbol in self.objetos_estaticos:
            pygame.draw.rect(pantalla, self.COLOR_ARBOL, arbol)
            pygame.draw.circle(pantalla, self.COLOR_COPA, (arbol.centerx, arbol.centery), 54)
        if self.planta_crecida:
            pygame.draw.rect(
                pantalla,
                self.COLOR_PLANTA,
                (self.residuo_contaminante.centerx - 4, self.residuo_contaminante.top - 18, 8, 18),
            )
            pygame.draw.circle(
                pantalla,
                self.COLOR_PLANTA,
                (self.residuo_contaminante.centerx - 8, self.residuo_contaminante.top - 18),
                8,
            )
            pygame.draw.circle(
                pantalla,
                self.COLOR_PLANTA,
                (self.residuo_contaminante.centerx + 8, self.residuo_contaminante.top - 18),
                8,
            )
        else:
            pygame.draw.rect(pantalla, self.COLOR_RESIDUO, self.residuo_contaminante)
        cuerpo_dron = self.dron.hurtbox
        color_dron = (
            self.COLOR_DRON_COOLDOWN
            if self.dron.cooldown_ataque > 0
            else self.COLOR_DRON
        )
        pygame.draw.rect(pantalla, color_dron, cuerpo_dron)
        pygame.draw.rect(pantalla, self.COLOR_DRON_DETALLE, cuerpo_dron, 3)
        pygame.draw.rect(
            pantalla,
            self.COLOR_DRON_DETALLE,
            (cuerpo_dron.x - 8, cuerpo_dron.centery - 3, 8, 6),
        )
        if self.eco.attackbox is not None:
            pygame.draw.rect(pantalla, self.COLOR_ATAQUE, self.eco.attackbox, 2)
        if self.dron.attackbox is not None:
            pygame.draw.rect(pantalla, self.COLOR_ATAQUE, self.dron.attackbox, 2)
        self.dibujar_cooldown_dron(pantalla)
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

    def dibujar_cooldown_dron(self, pantalla: pygame.Surface) -> None:
        """Muestra visualmente el tiempo restante antes del próximo ataque."""
        if self.dron.cooldown_ataque <= 0:
            return

        ancho_barra = self.dron.hitbox.width
        progreso = self.dron.cooldown_ataque / self.dron.COOLDOWN_ATAQUE
        fondo = pygame.Rect(self.dron.hitbox.left, self.dron.hitbox.top - 10, ancho_barra, 5)
        carga = pygame.Rect(
            fondo.left,
            fondo.top,
            round(ancho_barra * progreso),
            fondo.height,
        )
        pygame.draw.rect(pantalla, self.COLOR_DRON_DETALLE, fondo)
        pygame.draw.rect(pantalla, self.COLOR_DRON_COOLDOWN, carga)