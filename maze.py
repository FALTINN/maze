import pygame as pg
import numpy as np

pg.init()

TILE = 25
ticks = 60
player_x = 340
player_y = 340
player_r = 5
line_length = 15
sensors_amount = 6
robot_angle = 0
speed = 0.3
state = "go"
sensors_data = [0 for _ in range(sensors_amount)]
k_pos = 0.0015
k_d = 0.001
k_angle = 0.0005
previous_error = 0


maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # 0
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 1
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],  # 2
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],  # 3
    [1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0],  # 4  ← выход (29,4)
    [1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],  # 5
    [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1],  # 6
    [1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1],  # 7
    [1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1,0,1],  # 8
    [1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1],  # 9
    [1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1,0,1,0,1],  # 10
    [1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1],  # 11
    [1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1,0,1],  # 12
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0],  # 13
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # 14
]



screen = pg.display.set_mode((800, 400))
clock = pg.Clock()

def is_wall(cx, cy):
    if(cx < len(maze[0]) and cy < len(maze)):
        return maze[cy][cx]
    return False

def draw_maze():
    background = pg.Surface((len(maze[0])*TILE, len(maze) * TILE)).convert()
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:
                pg.draw.rect(background, (255, 255, 255), (x*TILE, y*TILE, TILE, TILE))
    return background

def draw_robot(color):
    pg.draw.circle(screen, color, (player_x, player_y), player_r)
    angle_step = ((360*np.pi)/(sensors_amount*180))
    angle = robot_angle - angle_step
    for i in range(sensors_amount):
        angle+=angle_step
        if(i == 0):
            pg.draw.line(screen, (0, 255, 0), (player_x, player_y), (player_x+line_length*np.cos(angle), player_y-line_length*np.sin(angle)))
            continue
        pg.draw.line(screen, color, (player_x, player_y), (player_x+line_length*np.cos(angle), player_y-line_length*np.sin(angle)))

def create_sensors():
    pass

def read_sensor(angle):
    for length in range(1000):
        if(is_wall(int((player_x+length*np.cos(angle))/TILE), int((player_y-length*np.sin(angle)) / TILE))):
            return length
    return 1000

def read_sensors():
    global sensors_data
    for i in range(sensors_amount):
        sensors_data[i] = (read_sensor(robot_angle+np.pi*2*(i)/sensors_amount))

def go_forward():
    global player_x, player_y, robot_angle
    player_x += speed * np.cos(robot_angle)
    player_y -= speed * np.sin(robot_angle)

def turn():
    global state
    global robot_angle
    robot_angle += 0.05

def align_robot():
    global robot_angle, k_pos, k_angle, previous_error, k_d
    left = (sensors_data[1] + sensors_data[2]) / 2
    right = (sensors_data[4] + sensors_data[5]) / 2
    error_center = k_pos*(left - right)
    error = k_pos*(left - right) + k_angle*(sensors_data[1] - sensors_data[2])
    # if(error_center > 0.2):
    #     error = k_pos*(left - right)
    error_dif = k_d * (error - previous_error)*ticks
    previous_error = error
    whole_error = error+error_dif
    whole_error = max(-0.01, min(whole_error, 0.01))
    robot_angle += ((whole_error)*np.pi)

background = draw_maze()
run = True
while run:
    screen.blit(background, (0,0))
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False
    draw_robot((255, 0, 0))
    read_sensors()
    match state:
        case "go":
            align_robot()
            go_forward()
            if(sensors_data[0] < 18):
                state = "turn"
        case "turn":
            turn()
            if(sensors_data[0] > 20):
                state = "go"

    pg.display.update()
    clock.tick(ticks)
pg.quit()