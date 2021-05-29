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


class TimerTrigger:
    '''
    A simple timer that is based on Frames per second.
    is_update will return true when its time to update
    '''
    def __init__(self, fps):
        self.fps_per_ms = 1000/fps
        self.last_ms = 0
    
    def get_millisecond(self):
        return time.perf_counter_ns() / 1000000
    
    def start(self):
        '''
            Call this when entering the game loop
        '''
        self.last_ms = self.get_millisecond()
        
    def is_update(self):
        '''
        Return True when its time to update
        else return False
        '''
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
        
        

if __name__ == "__main__":
    sense = SenseHat()
    sense.clear()
    
    player = Player(sense)
    enemiesList = EnemyList()
    algo_list = EnemyGenerationAlgoList()
    enemyGeneration1 = EnemyGeneration1(1)
    enemyGeneration2 = EnemyGeneration2(1)
    algo_list.algo.extend([enemyGeneration1, enemyGeneration2])
    #enemy = Enemy(x=0, y=4)
    
    #enemiesList.enemies.append(enemy)
    
    screen = Screen(sense, no_color)
    movementTimer = TimerTrigger(10)
    enemyTimer = TimerTrigger(2)
    enemyGenerationTimer = TimerTrigger(1)
    
    pressure = sense.get_pressure()
    print(pressure)

    sense.clear()

    temp = sense.get_temperature()
    print(temp)
    pre_direction = "CENTER"
    direction = ""
    movementTimer.start()
    enemyTimer.start()
    enemyGenerationTimer.start()
    try:
        while True:
            a = sense.get_accelerometer_raw()
            x = a['x']
            y = a['y']
            z = a['z']
            
            x = round(x, 3)
            y = round(y, 3)
            z = round(z, 3)
            
            if y > 0.1:
                direction = "LEFT"
            elif y < -0.1:
                direction = "RIGHT"
            else:
                direction = "CENTER"
            
            if direction != pre_direction:
                print(direction)
                pre_direction = direction
            
            if enemyGenerationTimer.is_update():
                if not algo_list.is_no_more_algo():
                    enemiesList.enemies.extend(algo_list.update())
                pass
            #Updates for the movement
            if enemyTimer.is_update():
                '''
                enemy.update()
                print("enemy", enemy.x, enemy.y)
                if enemy.destroy:
                    pass
                else:
                    screen.set_pixel(enemy.x, enemy.y, red)
                '''
                enemiesList.update()
            
            if movementTimer.is_update():
                player.move(direction)
            
            #Draw as fast as possible
            screen.clear_screen()
            enemiesList.draw(screen)
            screen.set_pixel(player.x, player.y, blue)
            screen.draw()
    except Exception as e:
        print_tb(sys.exc_info()[2])
    finally:
        clear = [no_color for i in range(64)]
        sense.set_pixels(clear)
    
    
    