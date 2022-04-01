"""
Traffic light simulation for Pico class.
2022 by Michael Ellis 
"""

import utime
import machine


def run():
    """
    Executes the traffic light control state machine
    """
    
    # Define the Pin connections. The red, amber and green
    # LEDs are on GP14, GP15 and GP16.
    redled = machine.Pin(14, machine.Pin.OUT)
    amberled = machine.Pin(15, machine.Pin.OUT)
    greenled = machine.Pin(16, machine.Pin.OUT)
    # The button is connected to GP17 and the buzzer to GP19
    button = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_DOWN)
    buzzer = machine.Pin(19, machine.Pin.OUT)

    # State variables for green light cycle.  We initialize the values
    # so that the program begins with the light green.
    green = True
    green_time = 2000 # milliseconds to keep green lit
    green_left = green_time # green_left keeps track of countdown
    redled.value(0)   # Off
    amberled.value(0) # Off
    greenled.value(1) # On
    
    # State variables for amber light
    amber = False
    amber_time = 1000 # 1000 msec to keep amber lit.
    amber_left = 0 
    
    # State variables for red light cycle
    red_time = green_time # Could be made different if desired
    red_left = 0
    
    # State variables for pedestrian crossing cycle.
    walking = False
    walk_requested = False
    walk_time = 2000
    walk_left = 0
    
    # State variables for audible signal during pedestrian crossings.
    beeping = False
    beep_time_on = 100
    beep_time_off = 400
    beep_left = 0
    
    polltime = 0.001 # Controls how long we sleep at the top of each loop.
    
    # Now that the variables are defined, start the control loop.
    # This implementation shows how to manage a slow loop that needs to handle
    # inputs that occur at random times without resorting to interrupts or
    # threading.
    while True: # This means "run forever"
        utime.sleep(polltime) # Check every 1 ms
        if button.value() == 1: 
            walk_requested = True # Pedestrian pushed the button.
            
        # Count down the green state    
        if green and green_left > 0:
            green_left -= 1
            if walk_requested:
                green_left = 0 # Short the countdown
            continue  # continue means "jump back to the top of the loop"
        
        # When we reach this point, it's time to transition from green to amber
        if green: 
            green=False
            greenled.value(0) # Turn green off
            amber=True
            amberled.value(1) # Turn amber on
            amber_left = amber_time # Reload the counter
            continue
    
        # Count down the amber state
        if amber and amber_left > 0:
            amber_left -= 1
            continue
        
        # Transition from amber to red
        if amber:
            amber=False
            amberled.value(0) # Off
            greenled.value(0) # Off (just to be sure)
            redled.value(1)   # On
            red_left = red_time  # Reload the red counter
            # If a pedestrian crossing has been requested, extend
            # the red time and start beeping.
            if walk_requested:
                red_left += walk_time
                walking = True
                beeping = True
                beep_left = beep_time_on
            walk_requested = False

        # Count down the red state.
        if red_left > 0:
            red_left -=1
            # Deal with pedestrian crossings
            if walking:
                if beep_left > 0:
                    beep_left -= 1
                else: # end of beep countdown
                    if beeping:
                       beeping = False
                       buzzer.value(0) # Off
                       beep_left = beep_time_off # Reload the counter
                    else:
                        beeping = True
                        buzzer.value(1) # On
                        beep_left = beep_time_on # Reload the counter
                                    
                walk_requested = False # Don't honor more than one request during a red cycle.
            else:
                if walk_requested:
                    red_left += walk_time
                    walking = True
                    beeping = True
                    beep_left = beep_time_on
                    
            continue
        
        # Red cycle finished. Transition to green.
        # Clear the walking and beeping flag variables
        walking = False
        beeping = False
        buzzer.value(0) # Off
        green=True     
        green_left = green_time # Reload green counter
        # Red and amber off, green on.
        redled.value(0)
        amberled.value(0)
        greenled.value(1)
        continue

# run() function ends here            

# The following functions are useful for checking the breadboard connections.
# They're not used in the run() function defined above.

def blink_led(pin, ntimes):
    """
    Blinks an LED connected to pin n times.
    """
    led = machine.Pin(pin, machine.Pin.OUT)
    for i in range(ntimes):
        led.value(1)
        utime.sleep(0.5)
        led.value(0)
        utime.sleep(0.5)

def read_button(pin):
    """
    Reads a 1 or 0 from a button connected to pin.
    """
    btn = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN)
    return btn.value()
           
        
        
        
        