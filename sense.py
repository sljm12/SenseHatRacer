'''
Driving game using SenseHat
'''
from sense_hat import SenseHat
from datetime import datetime as dt
import time

fps = 1000/1
fps_enemy = 1000/2
print("FPS", fps)
no_color = (0,0,0)

screen = []

print(screen)

class Screen:
    def __init__(self, sensehat):
        self.screen = [no_color for i in range(64)]
        self.sensehat = sensehat
    
    def clear_screen(self):
        self.screen = [no_color for i in range(64)]
        
    def draw(self):
        self.sensehat.set_pixels(self.screen)
    
    def set_pixel(self, x, y, color):
        self.screen[x+ y*8] = color
        

def get_millisecond():
    return time.perf_counter_ns() / 1000000

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
    screen = Screen(sense)
    
    pressure = sense.get_pressure()
    print(pressure)
    #sense.show_message(str(pressure))

    sense.clear()

    temp = sense.get_temperature()
    print(temp)
    pre_direction = "CENTER"
    direction = ""
    pre_time = get_millisecond()
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
            
        
        cur_time = get_millisecond()
        time_diff = cur_time - pre_time
        #print(time_diff, fps)
        
        #When its time to update execute this portion
        #How fast this updates its controled by the fps variable
        if time_diff > fps:
            pre_time = cur_time
            #print("Frame Reached", time_diff)
            player.move(direction)
            #player.draw()
            screen.clear_screen()
            screen.set_pixel(player.x, player.y, (255,0,0))
            screen.draw()
    
    
    