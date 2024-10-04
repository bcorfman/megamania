import arcade

class SpritePool:
    def __init__(self, sprites):
        self.sprites = sprites
        self.active_status = [False] * len(sprites)
        self.sprite_list = arcade.SpriteList()

    def request_sprite(self):
        for index, status in enumerate(self.active_status):
            if not status:
                self.active_status[index] = True
                self.sprite_list.append(self.sprites[index])
                return self.sprites[index]
        return None  # Return None if no inactive sprites are available

    def deactivate_sprite(self, sprite):
        if sprite in self.sprites:
            index = self.sprites.index(sprite)
            if self.active_status[index]:
                self.active_status[index] = False
                self.sprite_list.remove(sprite)

    def deactivate_all(self):
        for s in self.get_active_sprites():
            self.deactivate_sprite(s)

    def get_active_sprites(self):
        return [
            sprite for sprite, active in zip(self.sprites, self.active_status) if active
        ]

    def get_inactive_sprites(self):
        return [
            sprite
            for sprite, active in zip(self.sprites, self.active_status)
            if not active
        ]

    def update(self):
        self.sprite_list.update()

    def draw(self):
        self.sprite_list.draw()

