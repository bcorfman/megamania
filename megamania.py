import random
import time

import arcade

from collection import SpritePool

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 1960
SCREEN_TITLE = "Space Invaders-style Game"

SHIP_SCALE = 1.0
SHIP_SPEED = 10
LASER_SPEED = 20
LASER_SCALE = 1.0
ALIEN_SCALE = 0.8
ALIEN_SPEED = 15

MAX_LASERS = 12
LASER_COOLDOWN = 0.16

ALIEN_ROWS = 4
ALIENS_PER_ROW = 5
ALIEN_HORIZONTAL_SPACING = 400
ALIEN_VERTICAL_SPACING = SCREEN_HEIGHT * 2 / 3 / (ALIEN_ROWS - 1)


class Star:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.twinkling = False
        self.twinkle_color = None
        self.twinkle_duration = 0

    def update(self, window_height):
        self.y -= self.speed
        if self.y < 0:
            self.y = window_height

        if self.twinkling:
            self.twinkle_duration -= 1
            if self.twinkle_duration <= 0:
                self.twinkling = False
                self.twinkle_color = None
        elif random.random() < 0.001:
            self.twinkling = True
            self.twinkle_color = random.choice([arcade.color.RED, arcade.color.BLUE])
            self.twinkle_duration = random.randint(30, 90)

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.size, arcade.color.WHITE)
        if self.twinkling:
            twinkle_x = self.x + self.size * 1.2
            twinkle_y = self.y
            arcade.draw_circle_filled(
                twinkle_x, twinkle_y, self.size * 0.8, self.twinkle_color
            )


class Laser(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.angle = 270
        self.is_active = False

    def update(self, delta_time):
        if self.is_active:
            self.center_y += LASER_SPEED

    def reset(self, x, y):
        self.center_x = x
        self.center_y = y
        self.is_active = True


class Explosion(arcade.Sprite):
    def __init__(self, texture_list):
        super().__init__()
        self.current_texture = 0
        self.textures = texture_list
        self.scale = 1.0
        self.set_texture(self.current_texture)

    def update(self, delta_time):
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()


class Alien(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.movement_pattern = "diagonal_down"
        self.pattern_timer = 0

    def update(self, delta_time: float = 1 / 60):
        movement_speed = ALIEN_SPEED

        if self.movement_pattern == "diagonal_down":
            self.center_x += movement_speed / 2
            self.center_y -= movement_speed
        elif self.movement_pattern == "right":
            self.center_x += movement_speed

        self.pattern_timer += 1
        if self.pattern_timer >= 120:  # 2 seconds at 60 FPS
            self.pattern_timer = 0
            if self.movement_pattern == "diagonal_down":
                self.movement_pattern = "right"
            else:
                self.movement_pattern = "diagonal_down"

        # Wrap around screen edges
        if self.right < 0:
            self.left = SCREEN_WIDTH
        elif self.left > SCREEN_WIDTH:
            self.right = 0
        if self.top < 0:
            self.bottom = SCREEN_HEIGHT


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        arcade.set_background_color(arcade.color.BLACK)
        self.star_list = []
        self.ship_sprite = None
        self.ship_list = None
        self.lasers = None
        self.active_lasers = None
        self.alien_list = None
        self.explosion_list = None
        self.left_pressed = False
        self.right_pressed = False
        self.ctrl_pressed = False
        self.laser_sound = None
        self.explosion_sound = None
        self.last_fire_time = 0
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.start_time = 0
        self.life_icon_list = None
        self.player_exploding = False
        self.player_explosion_timer = 0
        self.reset_timer = 0
        self.explosion_textures = []
        self.game_over_text = arcade.Text(
            text="GAME OVER",
            x=self.width // 2,
            y=self.height // 2,
            color=arcade.color.WHITE,
            font_size=64,
            anchor_x="center",
        )
        self.enter_text = arcade.Text(
            text="Press ENTER to restart",
            x=self.width // 2,
            y=self.height // 2 - 64,
            color=arcade.color.WHITE,
            font_size=32,
            anchor_x="center",
        )

    def setup(self):
        self.generate_stars()
        self.ship_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png", SHIP_SCALE
        )
        self.ship_sprite.center_x = self.width // 2
        self.ship_sprite.center_y = self.ship_sprite.height
        self.ship_list = arcade.SpriteList()
        self.ship_list.append(self.ship_sprite)

        self.lasers = SpritePool(
            [
                Laser(":resources:images/space_shooter/laserBlue01.png", LASER_SCALE)
                for _ in range(MAX_LASERS)
            ]
        )
        self.alien_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.create_alien_formation()

        self.laser_sound = arcade.load_sound(":resources:sounds/laser1.wav")
        self.explosion_sound = arcade.load_sound(":resources:sounds/explosion1.wav")

        self.start_time = time.time()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.player_exploding = False
        self.player_explosion_timer = 0
        self.reset_timer = 0

        self.life_icon_list = arcade.SpriteList()
        for i in range(self.lives):
            life_icon = arcade.Sprite(
                ":resources:images/space_shooter/playerShip1_orange.png", 0.5
            )
            life_icon.center_x = 30 + i * 40
            life_icon.center_y = self.height - 30
            self.life_icon_list.append(life_icon)

        # Load explosion textures
        spritesheet = arcade.load_spritesheet(
            ":resources:images/spritesheets/explosion.png"
        )
        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        self.explosion_textures = spritesheet.get_texture_grid(
            size=(sprite_width, sprite_height), columns=columns, count=count
        )

    def create_alien_formation(self):
        self.alien_list = arcade.SpriteList()
        for row in range(ALIEN_ROWS):
            for col in range(ALIENS_PER_ROW):
                alien = Alien(":resources:images/enemies/bee.png", ALIEN_SCALE)
                alien.center_x = col * (self.width / ALIENS_PER_ROW) + (
                    self.width / (ALIENS_PER_ROW * 2)
                )
                alien.center_x += (row % 2) * ALIEN_HORIZONTAL_SPACING
                alien.center_y = (
                    SCREEN_HEIGHT
                    + ALIEN_VERTICAL_SPACING
                    + row * ALIEN_VERTICAL_SPACING
                )
                self.alien_list.append(alien)

    def generate_stars(self):
        num_stars = int((self.width * self.height) / 5000)
        self.star_list = []
        for _ in range(num_stars):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.uniform(1, 3)
            speed = random.uniform(0.5, 2)
            star = Star(x, y, size, speed)
            self.star_list.append(star)

    def on_draw(self):
        self.clear()
        for star in self.star_list:
            star.draw()
        self.ship_list.draw()
        self.lasers.draw()
        self.alien_list.draw()
        self.explosion_list.draw()

        self.score_text = arcade.Text(
            text=f"SCORE: {self.score}",
            x=self.width - 200,
            y=self.height - 30,
            color=arcade.color.WHITE,
            font_size=18,
        )        
        self.score_text.draw()
        self.life_icon_list.draw()

        if self.game_over:
            self.game_over_text.draw()
            self.enter_text.draw()

    def on_update(self, delta_time):
        if self.game_over:
            return

        if self.player_exploding:
            self.player_explosion_timer += 1
            if self.player_explosion_timer > 60:  # 1 second explosion
                self.player_exploding = False
                self.player_explosion_timer = 0
                self.reset_timer = 60  # 1 second delay before reset
                return

        if self.reset_timer > 0:
            self.reset_timer -= 1
            if self.reset_timer == 0:
                self.reset_after_death()
                return

        for star in self.star_list:
            star.update(self.height)

        if self.left_pressed and not self.right_pressed:
            self.ship_sprite.center_x -= SHIP_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.ship_sprite.center_x += SHIP_SPEED

        self.ship_sprite.center_x = max(
            self.ship_sprite.width // 2,
            min(self.ship_sprite.center_x, self.width - self.ship_sprite.width // 2),
        )

        self.lasers.update()
        for sprite in self.lasers.get_active_sprites():
            if sprite.bottom > self.height:
                self.lasers.deactivate_sprite(sprite)

        if self.ctrl_pressed:
            self.fire_laser()

        if time.time() - self.start_time > 2:  # Start alien movement after 2 seconds
            self.alien_list.update(delta_time)

        self.explosion_list.update(delta_time)

        for laser in self.lasers.get_active_sprites():
            hit_aliens = arcade.check_for_collision_with_list(laser, self.alien_list)
            for alien in hit_aliens:
                self.create_explosion(alien.center_x, alien.center_y)
                alien.remove_from_sprite_lists()
                self.score += 100
                self.lasers.deactivate_sprite(laser)

        for alien in self.alien_list:
            if not self.player_exploding and arcade.check_for_collision(alien, self.ship_sprite):
                self.lives -= 1
                alien.remove_from_sprite_lists()
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.start_player_explosion()
                if len(self.life_icon_list) > self.lives:
                    self.life_icon_list.pop().remove_from_sprite_lists()

    def fire_laser(self):
        current_time = time.time()
        if current_time - self.last_fire_time >= LASER_COOLDOWN:
            laser = self.lasers.request_sprite()
            if laser:
                laser.reset(self.ship_sprite.center_x, self.ship_sprite.top)
                arcade.play_sound(self.laser_sound)
                self.last_fire_time = current_time

    def start_player_explosion(self):
        self.player_exploding = True
        self.player_explosion_timer = 0
        self.create_explosion(self.ship_sprite.center_x, self.ship_sprite.center_y)
        self.ship_sprite.visible = False
        
    def create_explosion(self, x, y):
        explosion = Explosion(self.explosion_textures)
        explosion.center_x = x
        explosion.center_y = y
        self.explosion_list.append(explosion)
        arcade.play_sound(self.explosion_sound)

    def reset_after_death(self):
        self.ship_sprite.center_x = self.width // 2
        self.ship_sprite.center_y = self.ship_sprite.height
        self.ship_sprite.visible = True
        self.create_alien_formation()
        self.lasers.deactivate_all()

    def on_key_press(self, key, modifiers):
        if self.game_over and key == arcade.key.ENTER:
            self.setup()
            return

        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.LCTRL:
            self.ctrl_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.LCTRL:
            self.ctrl_pressed = False

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.generate_stars()
        if self.ship_sprite:
            self.ship_sprite.center_x = self.width // 2
            self.ship_sprite.center_y = self.ship_sprite.height


def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
