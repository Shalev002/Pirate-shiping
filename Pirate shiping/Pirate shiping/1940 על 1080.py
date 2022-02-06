from asyncio import events
from msilib.schema import Class
from operator import le
from pickle import TRUE
from tkinter import scrolledtext
import pygame
import os 
import time
import random

pygame.font.init()
pygame.mixer.init()

WIDTH = 1920
HEIGHT = 1080


WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pirate Ship')

s = 'sound'
music = pygame.mixer.music.load(os.path.join(s, 'Music.mp3'))
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound(os.path.join(s,'simple laser.mp3'))
monster_sound = pygame.mixer.Sound(os.path.join(s,'Die Sound Effect.mp3'))




#טעינת תמונות
RED_MONSTER = pygame.image.load(os.path.join('assests', 'pixel_ship_red_small.png'))
GREEN_MONSTER = pygame.image.load(os.path.join('assests', 'pixel_ship_green_small.png'))
BLUE_MONSTER = pygame.image.load(os.path.join('assests', 'pixel_ship_blue_small.png'))


#שחקן 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assests', 'pixel_ship_yellow.png'))

#יריות
RED_LASER = pygame.image.load(os.path.join('assests', 'pixel_laser_red.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assests', 'pixel_laser_yellow.png'))
BLUE_LASER = pygame.image.load(os.path.join('assests', 'pixel_laser_blue.png'))
GREEN_LASER = pygame.image.load(os.path.join('assests', 'pixel_laser_green.png'))

#קרע
BG = pygame.transform.scale(pygame.image.load(os.path.join('assests', 'background-black.png')), (WIDTH, HEIGHT))

score = 0
high_score = 0

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img 
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y < height  and self.y >= 0)

    def collision(self, ojb):
        return collide(self, ojb)

class Ship:
    COOLDOWN = 20

    def __init__(self,x , y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, objs):
        
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(objs):
                objs.health -= 10
                self.lasers.remove(laser)
            
    



    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)          
            self.lasers.append(laser)
            
            self.cool_down_counter = 1


    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    

    def move_lasers(self, vel, objs):
        global score
        global high_score
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):                        
                        objs.remove(obj)
                        score += 10
                        high_score += 10
                        if score < high_score:
                            high_score = score
                        monster_sound.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        

    



    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
   
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height()+ 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height()+ 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                'red': (RED_MONSTER, RED_LASER),
                'green': (GREEN_MONSTER, GREEN_LASER),
                'blue': (BLUE_MONSTER, BLUE_LASER)
                }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 10 , self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('arial.ttf', 60)
    lost_font = pygame.font.SysFont('arial.ttf', 60)
    shoot = False
    
    #מהירויות של מפלצות
    enemies = []
    wave_length = 2
    enemy_vel = 1
    

    #מהירויות של השחקן והלייזר
    player_vel = 12
    laser_vel = 5


    #מיקום השחקן
    player = Player(300, 930)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0


    def redraw_window():
        WIN.blit(BG, (0,0))

        
        lives_label = main_font.render(f'Lives: {lives}', 1, (49,200,90))
        level_label = main_font.render(f'Level: {level}', 1, (49,200,90))
        score_label = main_font.render(f'Score: {score}', 1, (49,200,90))
        high_label = main_font.render(f'HighScore: {high_score}', 1, (49,200,90))


        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10,10))
        WIN.blit(score_label, (900, 10))
        WIN.blit(high_label, (855, 60))

        for enemy in enemies:
            enemy.draw(WIN)        

        player.draw(WIN)



        if lost:
            lost_label = lost_font.render('You Die Loser!!', 1, (229,229,17))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        
             
        
        pygame.display.update()

        
    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        


        if len(enemies) == 0:
            level += 1
            player_vel += 1
            enemy_vel += 0.3
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'green', 'blue']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()



        key = pygame.key.get_pressed()
        if key[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if key[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if key[pygame.K_SPACE]:
            shoot = True  
            if shoot == True:
                player.shoot() 
                shoot_sound.play()
                shoot = False
                


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10          
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            



        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont('comicans', 70)
    run = True
    global score
    
    while run: 
            
        title_label = title_font.render('Press the mouse to begin...', 1, (229,229,17))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 450))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                score = 0
                main()
        

    pygame.quit()



main_menu()