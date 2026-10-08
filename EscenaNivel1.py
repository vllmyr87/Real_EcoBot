from dataclasses import dataclass
from pathlib import Path

import pygame

from Audio import GestorAudio
from Entidades import Eco, Enemigo
from GestorEscenas import EscenaBase


@dataclass
class ResiduoReciclable:
    """Residuo del escenario que se convierte en flor al tocarlo Eco."""

    hitbox: pygame.Rect
    reciclado: bool = False


class EscenaNivel1(EscenaBase):
    """Nivel cenital y panorámico con movimiento libre en dos dimensiones."""

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
    COLOR_PETALOS = (245, 112, 145)
    COLOR_CENTRO_FLOR = (255, 218, 86)
    COLOR_DRON_DEBIL = (119, 127, 119)
    COLOR_PANEL_PROGRESO = (30, 43, 39)
    COLOR_TEXTO_PROGRESO = (245, 245, 230)
    DANIO_DRON = 10
    RETROCESO_COLISION = 12
    ANCHO_PANTALLA = 800
    ALTO_PANTALLA = 600
    TAMANO_RESIDUO = 26
    POSICIONES_RESIDUOS = (
        (190, 120),
        (190, 430),
        (390, 100),
        (390, 275),
        (390, 460),
        (570, 110),
        (570, 275),
        (570, 455),
        (710, 220),
        (100, 430),
    )
    RUTA_AUDIO = Path(__file__).with_name("sound")
    RUTA_SFX_RECICLAJE = RUTA_AUDIO / "sonido_reciclaje_flor_exito.wav"
    RUTA_SFX_DESTRUCCION = RUTA_AUDIO / "sonido_dron_destruyendose.wav"

    def __init__(self) -> None:
        self.eco = Eco(100, 270, 34, 48)
        self.drones = [
            Enemigo(660, 120, 52, 48, objetivo=self.eco),
            Enemigo(660, 420, 52, 48, objetivo=self.eco),
        ]
        self.dron = self.drones[0]
        self.residuos = [
            ResiduoReciclable(
                pygame.Rect(x, y, self.TAMANO_RESIDUO, self.TAMANO_RESIDUO)
            )
            for x, y in self.POSICIONES_RESIDUOS
        ]
        self.objetos_estaticos = [
            pygame.Rect(300, 150, 90, 100),
            pygame.Rect(300, 350, 90, 100),
            pygame.Rect(485, 170, 70, 90),
            pygame.Rect(485, 350, 70, 90),
        ]
        self.gestor_audio = GestorAudio()
        self.explosiones_pendientes: list[tuple[int, int]] = []
        self.muerte_pendiente = False
        self.fuente_progreso = pygame.font.Font(None, 24)
        self.fuente_final = pygame.font.Font(None, 32)

    def mover_eco(self, dt: float) -> None:
        """Actualiza velocidades y resuelve el movimiento de Eco."""
        self.eco.preparar_actualizacion(dt)
        self.resolver_colisiones_aabb(dt)
        self.eco.actualizar_temporizador_invulnerable(dt)
        self.resolver_colision_eco_dron()
        self.resolver_reciclaje()

    def resolver_reciclaje(self) -> None:
        """Recicla automáticamente cada residuo que toca el hitbox de Eco."""
        for residuo in self.residuos:
            if (
                not residuo.reciclado
                and self.eco.hitbox.colliderect(residuo.hitbox)
            ):
                residuo.reciclado = True
                self.gestor_audio.reproducir_efecto(self.RUTA_SFX_RECICLAJE)

    def resolver_ataque_dron(self) -> None:
        """Aplica el daño del ataque del Dron cuando alcanza a Eco."""
        for dron in self.drones:
            if (
                not dron.cayendo
                and not dron.destruido
                and dron.attackbox is not None
                and dron.attackbox.colliderect(self.eco.hurtbox)
                and self.eco.temporizador_invulnerable <= 0
            ):
                self.eco.salud.recibir_danio(self.DANIO_DRON)
                self.eco.temporizador_invulnerable = 1.0
                return

    def resolver_colision_eco_dron(self) -> None:
        """Aplica daño e invulnerabilidad al contacto AABB entre ambas entidades."""
        for dron in self.drones:
            if dron.cayendo or dron.destruido:
                continue
            if not self.eco.hurtbox.colliderect(dron.hurtbox):
                continue

            if self.eco.temporizador_invulnerable <= 0:
                self.eco.salud.recibir_danio(self.DANIO_DRON)
                self.eco.temporizador_invulnerable = 1.0

            desplazamiento = self.eco.hurtbox.clip(dron.hurtbox)
            if desplazamiento.width < desplazamiento.height:
                desplazamiento_x = (
                    -self.RETROCESO_COLISION
                    if self.eco.hurtbox.centerx < dron.hurtbox.centerx
                    else self.RETROCESO_COLISION
                )
                self.eco.x += desplazamiento_x
            else:
                desplazamiento_y = (
                    -self.RETROCESO_COLISION
                    if self.eco.hurtbox.centery < dron.hurtbox.centery
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
        """Actualiza Eco, reciclaje, enemigos y victoria del nivel."""
        self.mover_eco(dt)
        pantalla = pygame.display.get_surface()
        ancho, alto = (
            pantalla.get_size()
            if pantalla is not None
            else (self.ANCHO_PANTALLA, self.ALTO_PANTALLA)
        )

        if all(residuo.reciclado for residuo in self.residuos):
            for dron in self.drones:
                if dron.cayendo or dron.destruido:
                    continue
                dron.iniciar_caida()
                self.gestor_audio.reproducir_efecto(self.RUTA_SFX_DESTRUCCION)

        for dron in self.drones:
            dron.establecer_limites_pantalla(ancho, alto)
            estaba_destruido = dron.destruido
            dron.actualizar(dt)
            if dron.destruido and not estaba_destruido:
                self.explosiones_pendientes.append(dron.hitbox.center)

        self.resolver_ataque_dron()
        if self.eco.salud.vida <= 0:
            self.muerte_pendiente = True

    def consumir_muerte_pendiente(self) -> bool:
        """Informa una sola vez que Eco perdió toda su salud."""
        muerte = self.muerte_pendiente
        self.muerte_pendiente = False
        return muerte

    def consumir_explosiones_pendientes(self) -> list[tuple[int, int]]:
        """Entrega al bucle principal los centros de los drones destruidos."""
        posiciones = self.explosiones_pendientes.copy()
        self.explosiones_pendientes.clear()
        return posiciones

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el nivel, los residuos, las flores y el progreso."""
        ancho, alto = pantalla.get_size()

        pantalla.fill(self.COLOR_FONDO)
        pygame.draw.rect(pantalla, self.COLOR_CAMINO, (0, 245, ancho, 70))
        pygame.draw.rect(pantalla, self.COLOR_CAMINO, (430, 0, 70, alto))
        pygame.draw.rect(pantalla, self.COLOR_AGUA, (0, 0, 175, 105))
        pygame.draw.rect(pantalla, self.COLOR_AGUA, (625, 495, 175, 105))
        for arbol in self.objetos_estaticos:
            pygame.draw.rect(pantalla, self.COLOR_ARBOL, arbol)
            pygame.draw.circle(pantalla, self.COLOR_COPA, (arbol.centerx, arbol.centery), 54)
        for residuo in self.residuos:
            if residuo.reciclado:
                self.dibujar_flor(pantalla, residuo.hitbox)
            else:
                pygame.draw.rect(pantalla, self.COLOR_RESIDUO, residuo.hitbox)

        for dron in self.drones:
            if dron.destruido:
                continue
            self.dibujar_dron(pantalla, dron)
            if dron.attackbox is not None:
                pygame.draw.rect(pantalla, self.COLOR_ATAQUE, dron.attackbox, 2)
            self.dibujar_cooldown_dron(pantalla, dron)

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

        residuos_reciclados = sum(residuo.reciclado for residuo in self.residuos)
        texto_progreso = self.fuente_progreso.render(
            f"RESIDUOS {residuos_reciclados}/{len(self.residuos)}",
            True,
            self.COLOR_TEXTO_PROGRESO,
        )
        panel = texto_progreso.get_rect(topright=(ancho - 20, 20)).inflate(24, 14)
        pygame.draw.rect(pantalla, self.COLOR_PANEL_PROGRESO, panel, border_radius=6)
        pantalla.blit(texto_progreso, texto_progreso.get_rect(center=panel.center))

        if residuos_reciclados == len(self.residuos):
            drones_destruidos = all(dron.destruido for dron in self.drones)
            mensaje = (
                "ECOSISTEMA RESTAURADO"
                if drones_destruidos
                else "DRONES DEBILITADOS"
            )
            texto_final = self.fuente_final.render(
                mensaje,
                True,
                self.COLOR_TEXTO_PROGRESO,
            )
            pantalla.blit(
                texto_final,
                texto_final.get_rect(center=(ancho // 2, 35)),
            )

    def dibujar_flor(self, pantalla: pygame.Surface, hitbox: pygame.Rect) -> None:
        """Representa el residuo reciclado como una flor pequeña."""
        centro_x = hitbox.centerx
        centro_y = hitbox.top + 9
        pygame.draw.line(
            pantalla,
            self.COLOR_PLANTA,
            (centro_x, centro_y + 3),
            (centro_x, hitbox.bottom - 2),
            3,
        )
        pygame.draw.ellipse(
            pantalla,
            self.COLOR_PLANTA,
            (centro_x - 10, centro_y + 8, 9, 5),
        )
        for desplazamiento_x, desplazamiento_y in (
            (0, -6),
            (-6, 0),
            (6, 0),
            (0, 6),
        ):
            pygame.draw.circle(
                pantalla,
                self.COLOR_PETALOS,
                (centro_x + desplazamiento_x, centro_y + desplazamiento_y),
                5,
            )
        pygame.draw.circle(
            pantalla,
            self.COLOR_CENTRO_FLOR,
            (centro_x, centro_y),
            4,
        )

    def dibujar_dron(self, pantalla: pygame.Surface, dron: Enemigo) -> None:
        """Dibuja el dron debilitado girando y encogiéndose mientras cae."""
        color_transparente = (1, 2, 3)
        superficie = pygame.Surface(dron.hitbox.size)
        superficie.fill(color_transparente)
        superficie.set_colorkey(color_transparente)
        cuerpo = superficie.get_rect()
        color = (
            self.COLOR_DRON_DEBIL
            if dron.cayendo
            else self.COLOR_DRON_COOLDOWN
            if dron.cooldown_ataque > 0
            else self.COLOR_DRON
        )
        pygame.draw.rect(superficie, color, cuerpo, border_radius=6)
        pygame.draw.rect(
            superficie,
            self.COLOR_DRON_DETALLE,
            cuerpo,
            3,
            border_radius=6,
        )
        pygame.draw.rect(
            superficie,
            self.COLOR_DRON_DETALLE,
            (0, cuerpo.centery - 3, 8, 6),
        )

        if dron.cayendo:
            factor = max(0.65, 1.0 - dron.tiempo_caida * 0.25)
            tamano = (
                max(1, round(cuerpo.width * factor)),
                max(1, round(cuerpo.height * factor)),
            )
            superficie = pygame.transform.smoothscale(superficie, tamano)
            superficie = pygame.transform.rotate(
                superficie,
                -min(35, round(dron.tiempo_caida * 50)),
            )

        pantalla.blit(superficie, superficie.get_rect(center=dron.hitbox.center))

    def dibujar_cooldown_dron(
        self,
        pantalla: pygame.Surface,
        dron: Enemigo,
    ) -> None:
        """Muestra visualmente el tiempo restante antes del próximo ataque."""
        if dron.cayendo or dron.cooldown_ataque <= 0:
            return

        ancho_barra = dron.hitbox.width
        progreso = dron.cooldown_ataque / dron.COOLDOWN_ATAQUE
        fondo = pygame.Rect(dron.hitbox.left, dron.hitbox.top - 10, ancho_barra, 5)
        carga = pygame.Rect(
            fondo.left,
            fondo.top,
            round(ancho_barra * progreso),
            fondo.height,
        )
        pygame.draw.rect(pantalla, self.COLOR_DRON_DETALLE, fondo)
        pygame.draw.rect(pantalla, self.COLOR_DRON_COOLDOWN, carga)