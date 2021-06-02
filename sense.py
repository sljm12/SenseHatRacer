'''
Driving game using SenseHat
'''
from sense_hat import SenseHat
from datetime import datetime as dt
import time
from random import randint
from traceback import print_exception, print_tb
import sys

no_color = (0,0,0)
light_grey = (128, 128, 128)
red = (255,0,0)
blue = (0,0,255)

class ExplosionAnimation:
    def __init__(self, x, y):
        self.start_yellow = (255,254,152)
        self.medium_orange = (255,137,82)
        self.end_orange = (231,106,48)
        self.stage = 0
        self.x = x
        self.y = y
    
    def update(self):
        self.stage = self.stage + 1
    
    def draw(self, screen):
        if self.stage == 0:
            screen.set_pixel(self.x, self.y, self.start_yellow)
        elif self.stage == 1:
            screen.set_pixel(self.x, self.y, self.medium_orange)
        elif self.stage == 2:
            screen.set_pixel(self.x, self.y, self.end_orange)
            
    def finished(self):
        return True if self.stage >2 else False


class GameOverAnimation:
    def __init__(self):
        self.stage = 0
        #Draw G
        self.game_over = [(1,7),(1,6),(1,5),(2,7),(3,7),(4,7),(5,7), (6,7), (6,6),(6,5),(5,5), (4,5)]
        #Draw O
        for x in range (1,7):
            for y in [3,1]:
                self.game_over.append((x,y))
        self.game_over.extend([(1,2),(6,2)])
    
    def update(self):
        self.stage = self.stage + 1
        
    def draw(self, screen):
        for i in self.game_over:
            screen.set_pixel(i[0],i[1], red)
    
    def finished(self):
        return True if self.stage >2 else False
    

class TimerTrigger:
    '''
    A simple timer that is based on Frames per second.
    is_update will return true when its time to update
    '''
    def __init__(self, fps):
        self.fps_per_ms = 1000/fps
        self.last_ms = 0
        self.pause_state = True
    
    def get_millisecond(self):
        return time.perf_counter_ns() / 1000000
    
    def start(self):
        '''
            Call this when entering the game loop
        '''
        self.last_ms = self.get_millisecond()
        self.pause_state = False
        
    def pause(self):
        self.pause_state = True
        
    def is_update(self):
        '''
        Return True when its time to update
        else return False
        '''
        if self.pause_state:
           return False
        else:
            curr_ms = self.get_millisecond()
            time_diff_ms = self.get_millisecond() - self.last_ms
            if time_diff_ms > self.fps_per_ms:
                self.last_ms = curr_ms
                return True
            else:
                return False

class Screen:
    def __init__(self, sensehat, bg_color):
        self.bg_color = bg_color
        self.screen = [bg_color for i in range(64)]
        self.sensehat = sensehat
    
    def clear_screen(self):
        self.screen = [self.bg_color for i in range(64)]
        
    def draw(self):
        self.sensehat.set_pixels(self.screen)
    
    def set_pixel(self, x, y, color):
        self.screen[x+ y*8] = color
    

#def get_millisecond():
#    return time.perf_counter_ns() / 1000000

#sense.show_message("Hello World")

class Player:
    def __init__(self, sensehat):
        self.x = 5
        self.y = 4
        self.sensehat = sensehat
        self.color =(255, 0, 0)
    
    def draw(self):
        #self.sensehat.set_pixel(self.x, self.y, self.color)
        pass
        
    def move(self, dir):
        if dir == "LEFT":
            self.y = 7 if (self.y+1) > 7 else self.y+1
        elif dir == "RIGHT":
            self.y = 0 if (self.y- 1) < 0 else self.y-1
        print(self.x,self.y)
    
    def check_collision(self, enemyList):
        for e in enemyList:
            if e.x == self.x and e.y == self.y:
                return True
        return False
        
class Enemy:
    def __init__(self,x=0, y=0):
        self.x = x
        self.y = y

        self.destroy = False
        
    def update(self):
        self.x = self.x + 1
        if self.x > 7:
            self.x = 7
            self.destroy = True
            

class EnemyList:
    def __init__(self):
        self.enemies = []
    
    def update(self):
        '''
        Updates the position of the enemies and remove those that are destroyed
        '''
        for i in self.enemies:
            i.update()
        #Remove those cars that are out of the screen
        self.enemies = [i for i in self.enemies if i.destroy == False]
    
    def draw(self, screen):
        for i in self.enemies:
            screen.set_pixel(i.x, i.y, red)
            
    def remove(self, x, y):
        for e in self.enemies:
            if e.x == x and e.y == y:
                self.enemies.remove(e)
            
class EnemyGeneration1:
    def __init__(self,waves):
        self.waves = waves
        self.current_wave = 0
        self.done = False
    
    def is_done(self):
        return self.done
    
    def update(self):
        start = randint(0, 7)
        self.current_wave = self.current_wave + 1
        if self.current_wave > self.waves:
            self.done = True
            return []
        else:
            return [Enemy(x=0, y=start)]
            
class EnemyGeneration2:
    '''
    Generates enemies by 2s, it first generates a number
    '''
    def __init__(self, waves):
        self.waves=waves
        self.current_wave = 0
        self.done = False
    
    def update(self):
        start = randint(0, 3)
        self.current_wave = self.current_wave + 1
        if self.current_wave > self.waves:
            self.done = True
            return []
        else:
            return [Enemy(x=0, y=start), Enemy(x=0,y=start+4)]
    
    def is_done(self):
        '''
        returns True if i have done finishing generating all the enemies under this algo
        '''
        return self.done
    
class EnemyGenerationAlgoList:
    def __init__(self):
        self.algo = []
        self.current_algo_num = 0
    
    def update(self):
        if self.is_no_more_algo():
            pass
        else:
            current_algo = self.algo[self.current_algo_num]
            r = current_algo.update()
            if current_algo.is_done():
                self.current_algo_num = self.current_algo_num + 1
            return r
        
    def is_no_more_algo(self):
        if self.current_algo_num >= len(self.algo):
            return True
        else:
            return False


def get_direction(sense):
    '''
    sense = SenseHat instance
    '''
    
    a = sense.get_accelerometer_raw()
    x = a['x']
    y = a['y']
    z = a['z']
    
    x = round(x, 3)
    y = round(y, 3)
    z = round(z, 3)
    
    if y > 0.1:
        return "LEFT"
    elif y < -0.1:
        return "RIGHT"
    else:
        return "CENTER"
    
def main_game(sense):
    lives = 3
    
    #sense = SenseHat()
    #sense.clear()
    player = Player(sense)
    enemiesList = EnemyList()
    algo_list = EnemyGenerationAlgoList()
    enemyGeneration1 = EnemyGeneration1(10)
    enemyGeneration2 = EnemyGeneration2(30)
    algo_list.algo.extend([enemyGeneration1, enemyGeneration2])
    explosionAnimation = None
    
    screen = Screen(sense, no_color)
    movementTimer = TimerTrigger(10)
    enemyTimer = TimerTrigger(5)
    enemyGenerationTimer = TimerTrigger(2)
    animationTimer = TimerTrigger(1)
    
    timerList = [movementTimer, enemyGenerationTimer, enemyTimer]

    pre_direction = "CENTER"
    direction = ""
    
    #Start Timers
    movementTimer.start()
    enemyTimer.start()
    enemyGenerationTimer.start()
    
    while True:
        direction = get_direction(sense)
        
        if direction != pre_direction:
            print(direction)
            pre_direction = direction
        
        if enemyGenerationTimer.is_update():
            if not algo_list.is_no_more_algo():
                enemiesList.enemies.extend(algo_list.update())
            pass
        #Updates for the movement
        if enemyTimer.is_update():
            enemiesList.update()
        
        if movementTimer.is_update():
            player.move(direction)
            if player.check_collision(enemiesList.enemies):
                print("Collide")
                enemiesList.remove(player.x, player.y)
                [t.pause() for t in timerList]
                explosionAnimation = ExplosionAnimation(player.x, player.y)
                lives = lives - 1
                if lives == 0:
                    return
                animationTimer.start()
                
        if animationTimer.is_update():
            print("Explosion Animation")
            explosionAnimation.update()
            if explosionAnimation.finished():
                print("Explosion Animation Finished")
                explosionAnimation = None
                animationTimer.pause()
                [t.start() for t in timerList]
        
        #Draw as fast as possible
        screen.clear_screen()
        enemiesList.draw(screen)
        screen.set_pixel(player.x, player.y, blue)
        if explosionAnimation is not None:
            explosionAnimation.draw(screen)
        screen.draw()
    
def game_over(sense):
    animationTimer = TimerTrigger(2)
    animationTimer.start()
    ga = GameOverAnimation()
    screen = Screen(sense, no_color)
    while True:
        if animationTimer.is_update():
            ga.update()
            if ga.finished():
                return
        ga.draw(screen)
        screen.draw()
    
        

if __name__ == "__main__":
    sense = SenseHat()
    sense.clear()
    #main_game(sense)
    game_over(sense)
    
    
