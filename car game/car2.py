import pygame
from pygame.locals import *
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# Create the window
screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# Colors
gray = (100, 100, 100)
red = (200, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
yellow = (224, 188, 43)
green = (76, 208, 56)
black = (0, 0, 0)
CITY_COLOR = (100, 100, 100)
DESERT_COLOR = (237, 201, 175)
FOREST_COLOR = (34, 139, 34)
SNOW_COLOR = (255, 250, 250)
DAY_COLOR = (135, 206, 250)
NIGHT_COLOR = (25, 25, 112)

# Road and marker sizes
road_width = 500  # Adjusted for 5 lanes
marker_width = 10
marker_height = 50

# Lane coordinates
lane_width = road_width // 5
lanes = [(SCREEN_WIDTH // 2 - road_width // 2 + i * lane_width + lane_width // 2) for i in range(5)]

# Road and edge markers
road = (SCREEN_WIDTH // 2 - road_width // 2, 0, road_width, SCREEN_HEIGHT)
left_edge_marker = (road[0] - marker_width, 0, marker_width, SCREEN_HEIGHT)
right_edge_marker = (road[0] + road_width, 0, marker_width, SCREEN_HEIGHT)

# For animating movement of the lane markers
lane_marker_move_y = 0

# Player's starting coordinates
player_x = lanes[2]  # Start in the middle lane
player_y = 400

# Frame settings
clock = pygame.time.Clock()
fps = 120

# Game settings
gameover = False
speed = 2
score = 0
high_score = 0

# Load sound effects
car_sound = pygame.mixer.Sound('sounds/rain-inside-a-car-113602.wav')
crash_sound = pygame.mixer.Sound('sounds/crash-7075.wav')
horn_sound = pygame.mixer.Sound('sounds/car-horn-3-191449.wav')

# Track themes
themes = {
    'city': CITY_COLOR,
    'desert': DESERT_COLOR,
    'forest': FOREST_COLOR,
    'snow': SNOW_COLOR
}

# Current theme and day/night cycle
current_theme = 'city'
cycle_color = DAY_COLOR
cycle_time = 0
weather = 'clear'
snowflakes = []

# Function to draw the track
def draw_track(theme, cycle_color):
    screen.fill(themes[theme])
    screen.fill(cycle_color, special_flags=pygame.BLEND_MULT)

# Function to draw the weather (snow)
def draw_weather():
    global snowflakes
    if weather == 'snow':
        for flake in snowflakes:
            flake[1] += flake[2]
            if flake[1] > SCREEN_HEIGHT:
                flake[1] = random.randrange(-50, -10)
                flake[0] = random.randrange(0, SCREEN_WIDTH)
            pygame.draw.circle(screen, (255, 255, 255), flake[:2], flake[3])

# Vehicle class for player and other vehicles
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (int(new_width), int(new_height)))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

# Player vehicle class
class PlayerVehicle(Vehicle):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)

# Raindrop class for rain effect
class RainDrop(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 10))
        self.image.fill(blue)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(-SCREEN_HEIGHT, 0)
        self.speed_y = 5

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = random.randint(-SCREEN_HEIGHT, 0)
            self.rect.x = random.randint(0, SCREEN_WIDTH)

# Power-up class
class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(yellow)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed_y = 5

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, red, (25, 25), 25)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed_y = 5

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Sprite groups for different objects
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()
rain_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

# Load the vehicle images
vehicle_images = []
for image_filename in ['car.png', 'pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)

# Load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# Start the car sound
car_sound.play(loops=-1)  # -1 loops infinitely

# Car selection screen
car_selection = True
selected_car = 0
car_images = [pygame.transform.scale(image, (100, 100)) for image in vehicle_images]

# Grass color selection
grass_colors = [green, yellow]
selected_grass_color = 0

# Car selection loop
while car_selection:
    screen.fill(grass_colors[selected_grass_color])
    font = pygame.font.Font(None, 36)
    text = font.render("Select Your Car", True, white)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(text, text_rect)

    for i, image in enumerate(car_images):
        rect = image.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 120))
        screen.blit(image, rect)
        if i == selected_car:
            pygame.draw.rect(screen, blue, rect, 3)

    # Display grass color options
    font = pygame.font.Font(None, 24)
    grass_text = font.render("Select Grass Color using arrows: ", True, black)
    grass_text_rect = grass_text.get_rect(center=(SCREEN_WIDTH // 2 + 170, 500))
    screen.blit(grass_text, grass_text_rect)

    for i, color in enumerate(["Yellow", "Green"]):
        color_text = font.render(color, True, black)
        color_text_rect = color_text.get_rect(center=(SCREEN_WIDTH // 2 + 170, 530 + i * 30))
        screen.blit(color_text, color_text_rect)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                selected_car = (selected_car - 1) % len(car_images)
            elif event.key == K_DOWN:
                selected_car = (selected_car + 1) % len(car_images)
            elif event.key == K_LEFT:
                selected_grass_color = (selected_grass_color - 1) % len(grass_colors)
            elif event.key == K_RIGHT:
                selected_grass_color = (selected_grass_color + 1) % len(grass_colors)
            elif event.key == K_RETURN:
                car_selection = False

# Create player vehicle and add to group
selected_car_image = vehicle_images[selected_car]
player = PlayerVehicle(selected_car_image, player_x, player_y)
player_group.add(player)

# Create raindrops for rain effect
for _ in range(100):
    rain_drop = RainDrop()
    rain_group.add(rain_drop)

# Function to move vehicles aside when horn is used
def move_vehicles_aside():
    for vehicle in vehicle_group:
        if vehicle.rect.centerx < SCREEN_WIDTH // 2:
            vehicle.rect.x = max(vehicle.rect.x - 50, road[0])
        else:
            vehicle.rect.x = min(vehicle.rect.x + 50, road[0] + road_width - vehicle.rect.width)

# Function to spawn power-ups
def spawn_powerup():
    if random.randint(1, 100) <= 1:  # Reduced the probability
        powerup = Powerup(random.choice(lanes), SCREEN_HEIGHT / -2)
        powerup_group.add(powerup)

# Function to spawn obstacles
def spawn_obstacle():
    if random.randint(1, 100) <= 1:  # Reduced the probability
        obstacle = Obstacle(random.choice(lanes), SCREEN_HEIGHT / -2)
        obstacle_group.add(obstacle)

# Game loop
running = True
while running:
    clock.tick(fps)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        horn_playing = False
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                if player.rect.left > lanes[0]:
                    player.rect.x -= lane_width
            elif event.key == K_RIGHT:
                if player.rect.right < lanes[-1]:
                    player.rect.x += lane_width
            elif event.key == K_SPACE and not horn_playing:
                horn_sound.play()
                move_vehicles_aside()
                horn_playing = True
            elif event.key == pygame.K_1:
                current_theme = 'city'
            elif event.key == pygame.K_2:
                current_theme = 'desert'
            elif event.key == pygame.K_3:
                current_theme = 'forest'
            elif event.key == pygame.K_4:
                current_theme = 'snow'
            elif event.key == pygame.K_d:
                cycle_color = DAY_COLOR
            elif event.key == pygame.K_n:
                cycle_color = NIGHT_COLOR
            elif event.key == pygame.K_w:
                weather = 'snow' if weather == 'clear' else 'clear'
                if weather == 'snow':
                    if any(isinstance(sprite, RainDrop) for sprite in rain_group):
                        rain_group.empty()  # Remove existing raindrops
                    snowflakes = [[random.randrange(0, SCREEN_WIDTH), random.randrange(-50, SCREEN_HEIGHT), random.randint(1, 3), random.randint(1, 3)] for _ in range(100)]
        elif event.type == KEYUP:
            if event.key == K_SPACE:
                horn_sound.stop()
                horn_playing = False

    # Draw track and weather
    draw_track(current_theme, cycle_color)
    draw_weather()

    # Draw road and edge markers
    pygame.draw.rect(screen, gray, road)
    pygame.draw.rect(screen, white, left_edge_marker)
    pygame.draw.rect(screen, white, right_edge_marker)
    
    # Animate lane markers
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, SCREEN_HEIGHT, marker_height * 2):
        for i in range(1, 5):
            lane_x = SCREEN_WIDTH // 2 - road_width // 2 + i * lane_width
            pygame.draw.rect(screen, white, (lane_x, y + lane_marker_move_y, marker_width, marker_height))

    # Draw player vehicle
    player_group.draw(screen)

    # Add new vehicles if needed
    if len(vehicle_group) < 2:
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:
            lane_center = random.choice(lanes)
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane_center, SCREEN_HEIGHT / -2)
            vehicle_group.add(vehicle)

    # Update vehicle positions
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        if vehicle.rect.top >= SCREEN_HEIGHT:
            vehicle.kill()
            score += 1
            if score > 0 and score % 5 == 0:
                speed += 1

    # Spawn power-ups and obstacles
    spawn_powerup()
    spawn_obstacle()

    # Update and draw power-ups and obstacles
    powerup_group.update()
    obstacle_group.update()
    
    vehicle_group.draw(screen)
    rain_group.update()
    rain_group.draw(screen)
    powerup_group.draw(screen)
    obstacle_group.draw(screen)

    # Display score
    font = pygame.font.Font(None, 36)
    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect(center=(50, 30))
    screen.blit(text, text_rect)

    # Check for collisions
    if pygame.sprite.spritecollide(player, vehicle_group, True) or pygame.sprite.spritecollide(player, obstacle_group, True):
        gameover = True
        crash_sound.play()
        car_sound.stop()
        crash_rect.center = [player.rect.center[0], player.rect.top]
    
    if pygame.sprite.spritecollide(player, powerup_group, True):
        speed = max(1, speed - 1)

    # Handle game over
    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, SCREEN_WIDTH, 100))
        font = pygame.font.Font(None, 36)
        text = font.render('Game over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, 100))
        screen.blit(text, text_rect)

    # Update display
    pygame.display.update()

    while gameover:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    powerup_group.empty()
                    obstacle_group.empty()
                    player.rect.center = [player_x, player_y]
                    car_sound.play(loops=-1)
                elif event.key == K_n:
                    gameover = False
                    running = False

# Quit Pygame
pygame.quit()
sys.exit()