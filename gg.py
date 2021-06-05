"""
  Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1152
SCREEN_HEIGHT = 896
SCREEN_TITLE = "Platformer"
SPRITE_PIXEL_SIZE = 128
TILE_SCALING = 0.5
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement of player
MOVEMENT_SPEED = 8
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Position of player
PLAYER_START_X = 256
PLAYER_START_Y = 192

# Viewpoint margin
LEFT_VIEWPORT_MARGIN = 50
RIGHT_VIEWPORT_MARGIN = 300
TOP_VIEWPORT_MARGIN = 150
BOTTOM_VIEWPORT_MARGIN = 150


class MyGame(arcade.View):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        # super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.wall_list = None
        self.coin_list = None
        self.background = None
        self.goal = None

        # Set up the player
        self.player_sprite = None

        # Add physics engine
        self.physics_engine = None

        self.end_of_map = 0
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.view_left = 0
        self.view_bottom = 0

        self.score = 0
        self.level = 1

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        self.player_list = arcade.SpriteList()
        if not self.player_sprite:
            self.player_sprite = self.create_player_sprite()
            self.player_list.append(self.player_sprite)

        # add map to game
        my_map = arcade.tilemap.read_tmx("my_map1.tmx")
        self.background = arcade.tilemap.process_layer(map_object=my_map, layer_name="back_objects")
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map, layer_name="ground")
        self.goal = arcade.tilemap.process_layer(map_object=my_map, layer_name="goal")
        self.coin_list = arcade.tilemap.process_layer(map_object=my_map, layer_name="collectable")

        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        self.map_width = (my_map.map_size.width - 1) * my_map.tile_size.width

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

        # Reset the viewport
        self.view_left = 0
        self.view_bottom = 0

    def create_player_sprite(self) -> arcade.AnimatedWalkingSprite:
        """Creates the animated player sprite

        Returns:
            The properly set up player sprite
        """
        # Where are the player images stored?
        texture_path = ":resources:images/animated_characters/female_adventurer/"

        # Set up the appropriate textures
        walking_paths = [texture_path + f"femaleAdventurer_walk{x}.png" for x in range(0, 7)]
        standing_path = texture_path + "femaleAdventurer_idle.png"
        jumping_path = texture_path + "femaleAdventurer_jump.png"

        # Load them all now
        walking_right_textures = [arcade.load_texture(texture) for texture in walking_paths]
        walking_left_textures = [arcade.load_texture(texture, mirrored=True) for texture in walking_paths]

        standing_right_textures = [arcade.load_texture(standing_path)]
        standing_left_textures = [arcade.load_texture(standing_path, mirrored=True)]

        jumping_right_textures = [arcade.load_texture(jumping_path)]
        jumping_left_textures = [arcade.load_texture(jumping_path, mirrored=True)]

        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the proper textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.jumping_right_textures = jumping_right_textures
        player.jumping_left_textures = jumping_left_textures

        # Move the player sprite back to the beginning
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT

        # Set the initial texture
        player.texture = player.stand_right_textures[0]

        return player

    def scroll_viewport(self) -> None:
        """Scrolls the viewport when the player gets close to the edges"""
        # Scroll left
        # Find the current left boundary
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN

        # Are we to the left of this boundary? Then we should scroll left.
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            # But don't scroll past the left edge of the map
            if self.view_left < 0:
                self.view_left = 0

        # Scroll right
        # Find the current right boundary
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN

        # Are we to the right of this boundary? Then we should scroll right.
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            # Don't scroll past the right edge of the map
            if self.view_left > self.map_width - SCREEN_WIDTH:
                self.view_left = self.map_width - SCREEN_WIDTH

        self.view_bottom = int(self.view_bottom)
        self.view_left = int(self.view_left)

        # Do the scrolling
        arcade.set_viewport(
            left=self.view_left,
            right=SCREEN_WIDTH + self.view_left,
            bottom=self.view_bottom,
            top=SCREEN_HEIGHT + self.view_bottom,
        )

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        self.background.draw()
        self.wall_list.draw()
        self.goal.draw()
        self.coin_list.draw()
        self.player_list.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, start_x=10 + self.view_left,
                         start_y=820 + self.view_bottom, color=arcade.csscolor.GOLD, font_size=40)

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                # play sound

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """
        # Move the player with the physics engine
        self.physics_engine.update()

        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.view_left = 0
            self.view_bottom = 0

        self.scroll_viewport()
        self.player_sprite.update_animation(delta_time)

        collected_coins = arcade.check_for_collision_with_list(
            sprite=self.player_sprite, sprite_list=self.coin_list)

        for coin in collected_coins:
            # Add the coin score to our score
            self.score += 1
            # self.score += int(coin.properties["point_value"])
            coin.remove_from_sprite_lists()

        # goals_hit = arcade.check_for_collision_with_list(
        #     sprite=self.player_sprite, sprite_list=self.goals
        # )


def main():
    """ Main method """
    window = MyGame()
    start_view = StartView()
    start_view.setup()
    window.show_view.setup()
    arcade.run()


100
101


def main():
    102
    """ Main method """


103
104
window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
105
start_view = GameView()
106
window.show_view(start_view)
107
start_view.setup()
108
arcade.run()
109

if __name__ == "__main__":
    main()

