'''
Driving game using SenseHat
'''
from sense_hat import SenseHat
from datetime import datetime as dt
import time


no_color = (0,0,0)
light_grey = (128, 128, 128)


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
    def __init__(self):
        self.x = 0
        self.y = 0
        self.time_update_factor = 2
        self.previous_time_ns = get_millsecond()
        
    def update(self):
        pass
        

if __name__ == "__main__":
    sense = SenseHat()
    sense.clear()
    player = Player(sense)
    screen = Screen(sense, light_grey)
    movementTimer = TimerTrigger(10)
    
    pressure = sense.get_pressure()
    print(pressure)
    #sense.show_message(str(pressure))

    sense.clear()

    temp = sense.get_temperature()
    print(temp)
    pre_direction = "CENTER"
    direction = ""
    #pre_time = get_millisecond()
    movementTimer.start()
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
                
            
            if movementTimer.is_update():
                player.move(direction)
                screen.clear_screen()
                screen.set_pixel(player.x, player.y, (255,0,0))
                screen.draw()
    except:
        pass
    finally:
        clear = [no_color for i in range(64)]
        sense.set_pixels(clear)
    
    
    