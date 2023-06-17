#! python3


# Python File for LED-STRIPS
# AUTHOR: Lorenz Schreyer
# FIRST DATE: 19.12.2019
# Repo: https://github.com/lorenzschreyer/playground
#
#    _     _____     ____  ____   ___   ___    __ __    __ ______  ____  ___   ____  
#   | |   / ___/    |    \|    \ /   \ |   \  |  |  |  /  ]      ||    |/   \ |    \ 
#   | |  (   \_     |  o  )  D  )     ||    \ |  |  | /  /|      | |  ||     ||  _  |
#   | |___\__  |    |   _/|    /|  O  ||  D  ||  |  |/  / |_|  |_| |  ||  O  ||  |  |
#   |     /  \ |    |  |  |    \|     ||     ||  :  /   \_  |  |   |  ||     ||  |  |
#   |     \    |    |  |  |  .  \     ||     ||     \     | |  |   |  ||     ||  |  |
#   |_____|\___|    |__|  |__|\_|\___/ |_____| \__,_|\____| |__|  |____|\___/ |__|__|
#

# Librarys
import board
import sys
import time
import sqlite3
import threading
import random

# neopixel Library
# https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel
import neopixel




# class CHECKSTOP
# Continously check DB table pixel for changes in a Thread
class CHECKSTOP(threading.Thread):
    
    # Initialization of Thread
    def __init__(self, verbose=False):
        
        threading.Thread.__init__(self)
        
        self.tablePixelName = "pixel"
        
        self.checkstop = True
        self.isRunning = True
        
        # Connecting to Database
        self.con = sqlite3.connect("/home/pi/sqlite3/smarthome")
        self.cursor = self.con.cursor()
        
        # Verbose option (default False)
        self.V = verbose
        
        # Start Thread
        self.start()
        
        # verbose print
        if self.V:
            print("Started Thread CHECKSTOP")
    
    # Method run()
    # runs continously since Thread is started
    # checks the Database as fast as its possible
    def run(self):
            
        while self.isRunning:
            
            try:
                # Connecting to Database
                con = sqlite3.connect("/home/pi/sqlite3/smarthome")
                cursor = con.cursor()

                # Fetching stop state in table pixel
                cursor.execute("SELECT state FROM " + self.tablePixelName + " WHERE ID = 2")
                result = (cursor.fetchall()[0][0])

                # Updating self.checkstop
                if result == 1:
                    self.checkstop = True
                if result == 0:
                    self.checkstop = False

                con.close()
            except:
                print("ERROR: " + str(sys.exc_info()))
            
    # Method sleep(delay)
    # sleeps amount of time while listening to Database
    def sleep(self, delay):
        
        # sleeps for delay * 100 -> 10ms
        for i in range(round(delay*100)):
            if self.checkstop:
                time.sleep(0.01)
        
        # verbose print
        if self.V:
            print("executed CHECKSTOP.sleep(): (sleeped: " + str(delay) + "s)")
            
            
    # Method terminate()
    # terminates the Thread
    def terminate(self):
        
        self.con.close()
        self.isRunning = False
        
        # verbose print
        if self.V:
            print("terminated Thread Checkstop")


# Class DATABASE
# Fetching and Inserting Data into DB
class DATABASE:
    
    # Initialization
    def __init__(self, strip, verbose=False):
            
        # Table names
        self.tablePreferencesName = "preferences"
        self.tablePixelName = "pixel"
        self.tableStripName = "stripValues"
        
        #Ledstrip
        self.LedStrip = strip.LedStrip
        self.stripFrom = strip.stripFrom
        self.stripTo = strip.stripTo
        self.pixelCount = strip.pixelCount
        
        # Verbose option (default False)
        self.V = verbose
        
        # Database
        self.con = sqlite3.connect("/home/pi/sqlite3/smarthome")
        self.cursor = self.con.cursor()
        
        # First Declaration of following Arrays
        self.DBpixels = []
        self.r = []
        self.g = []
        self.b = []         
        
        self.DBpixelsFull = []
        self.rFull = []
        self.gFull = []
        self.bFull = []        
        
        # Fetching table preferences
        self.cursor.execute("SELECT setting FROM " + self.tablePreferencesName)
        self.DBpreferences = (self.cursor.fetchall())
        
        
        ###############
        # Preferences #
        ###############
        
        if (self.LedStrip == 0 or self.LedStrip == 1):
            # Value (0 - 255) for each
            # r,g,b values of first strip
            self.gradient1 = self.DBpreferences[0][0]
            self.gradient2 = self.DBpreferences[1][0]
            self.gradient3 = self.DBpreferences[2][0]
            self.gradient4 = self.DBpreferences[3][0]
            self.gradient5 = self.DBpreferences[4][0]
            self.gradient6 = self.DBpreferences[5][0]
            
        elif (self.LedStrip == 2):
            # Value (0 - 255) for each
            # r,g,b values of second strip
            self.gradient1 = self.DBpreferences[6][0]
            self.gradient2 = self.DBpreferences[7][0]
            self.gradient3 = self.DBpreferences[8][0]
            self.gradient4 = self.DBpreferences[9][0]
            self.gradient5 = self.DBpreferences[10][0]
            self.gradient6 = self.DBpreferences[11][0]
        
        
        # Value (0 - 10) in 0.1 steps
        # Time it takes to fade to new Lighting
        self.transitionspeed = self.DBpreferences[12][0]
        
        # Value (0 - 10) in 0.1 steps
        # Delay after a Fade to new Lighting
        self.delay = self.DBpreferences[13][0]
        
        # Value (0 - 2)
        # 0 --> Fade
        # 1 --> Linear
        # 2 --> Gradient
        # Type it fades to new Lighting
        self.transitiontype = self.DBpreferences[14][0]
        
        # Value (0.1 - 5) in 0.1 steps
        # Speed of Blinking
        self.blinkspeed = self.DBpreferences[15][0]
        
        # Value (0 - 10)
        # Speed how fast a Rainbow cycles
        self.rainbowspeed = self.DBpreferences[16][0]
        
        # Value (0 - 3)
        # 0 --> Standard
        # 1 --> Erotic
        # 2 --> Lucky
        # 3 --> Sea
        # Mood of Autochange the Lighting
        self.mood = self.DBpreferences[17][0]
        
        # Value (0 - 4)
        # 0 --> Color
        # 1 --> Gradient
        # 2 --> Autochange
        # 3 --> Blink
        # 4 --> Rainbow
        # Profile which establishes whats the new Lighting like
        self.profile = self.DBpreferences[18][0]
        
        # Get Data of every pixel from Database
        self.getStrip()
        
        # verbose print
        if self.V:
            print("Initializing class DATABASE")
        
    # Method updateCheckstop()
    # Updates the checkstop to 0 in table pixel
    def updateCheckstop(self, value):
        
        try:
            # Starts measurement of time
            s = time.time()

            # Updating stop to 0 in Database
            self.cursor.execute("UPDATE " + self.tablePixelName + " SET state = " + str(value) + " WHERE ID = 2")
            self.con.commit()

            # Get Data of every pixel from Database
            self.getStrip()
        except:
            print("ERROR: " + str(sys.exc_info()))
        
        
        # verbose print
        if self.V:
            
            # Stops measurement of time
            t = str(round(time.time() - s, 3 ))
            
            print("executed DATABASE.updateCheckstop(" + str(value) + "): (took " + t + "s)")

    # Method updatePower(state)
    # Updates the power to 0 / 1 in table pixel
    def updatePower(self, state):  
        
        # Starts measurement of time
        s = time.time()
        
        # Updating stop to 0 in Database
        if self.LedStrip == 0:
            self.cursor.execute("UPDATE " + self.tablePixelName + " SET state = " + str(state) + " WHERE ID = 3")
            self.cursor.execute("UPDATE " + self.tablePixelName + " SET state = " + str(state) + " WHERE ID = 4")
            
        if self.LedStrip == 1:
            self.cursor.execute("UPDATE " + self.tablePixelName + " SET state = " + str(state) + " WHERE ID = 3")
            
        if self.LedStrip == 2:
            self.cursor.execute("UPDATE " + self.tablePixelName + " SET state = " + str(state) + " WHERE ID = 4")
            
        self.con.commit()
        
        # Get Data of every pixel from Database
        self.getStrip()
        
        
        # verbose print
        if self.V:
            
            # Stops measurement of time
            t = str(round(time.time() - s, 3 ))
            
            print("executed DATABASE.updatePower(" + str(self.LedStrip) + ", " + str(state) + "): (took " + t + "s)")
    
    # Method updateStrip(pixelNum, pixels)
    # Updates the r, g, b values in table stripValues
    def updateStrip(self, pixels):
        
        # Starts measurement of time
        s = time.time()
        
        # Updates r,g,b Values on position [i]
        for i in range(self.pixelCount):
            self.cursor.execute("UPDATE " + self.tableStripName + " SET r = " + (str(pixels[i])[1:-1]).split(',')[0] + ", g = " + (str(pixels[i])[1:-1]).split(',')[1] + ", b = " + (str(pixels[i])[1:-1]).split(',')[2] + " WHERE ID = " + str(i))
            
        self.con.commit()
        
        # Get Data of every pixel from Database
        self.getStrip()
        
        
        # verbose print
        if self.V:
            # Stops measurement of time
            t = str(round(time.time() - s, 3 ))
            
            print("executed DATABASE.updateStrip(): (took " + t + "s)")
    
    # Method getStrip()
    # Update attributes from Database
    def getStrip(self):
        
        # Starts measurement of time
        s = time.time()
        
        self.r = []
        self.g = []
        self.b = []        
        self.rFull = []
        self.gFull = []
        self.bFull = []
        
        # Fetching table strip
        self.cursor.execute("SELECT r, g, b FROM " + self.tableStripName)
        self.DBpixelsFull = (self.cursor.fetchall())
        
        # Appending Values to Full Arrays
        for i in range(len(self.DBpixelsFull)):
            self.rFull.append(self.DBpixelsFull[i][0])
            self.gFull.append(self.DBpixelsFull[i][1])
            self.bFull.append(self.DBpixelsFull[i][2])
        
        # Appending Values to rgb Arrays
        for i in range(self.stripFrom, self.stripTo):
            self.r.append(self.DBpixelsFull[i][0])
            self.g.append(self.DBpixelsFull[i][1])
            self.b.append(self.DBpixelsFull[i][2])
            
    
        # verbose print
        if self.V:
            
            # Stops measurement of time
            t = str(round(time.time() - s, 3 ))
            
            print("executed DATABASE.getStrip(): (took " + t + "s)")
    
    # Method terminate()
    # closes Database safely
    def terminate(self):
        
#        self.updateCheckstop(1)
        self.con.close()
        
        # verbose print
        if self.V:
            print("terminated Database")
        

# Class STRIP
# Controlling Ledstrip
class STRIP:
    
    # Initialization
    def __init__(self, LedStrip, verbose=False):
        
        # Verbose option (default False)
        self.V = verbose
        
        self.pixelCount = 310
        self.LedStrip = LedStrip
        
        # Values for Full Ledstrip
        # 310 Leds
        if self.LedStrip == 0:

            # Number of Pixels the Strip haves
            self.stripTo = 310
            self.stripFrom = 0
            self.pixelNum = 310        
            
        # Values for LedStrip 1
        # 144 Leds
        if self.LedStrip == 1:

            # Number of Pixels the Strip haves
            self.stripTo = 144
            self.stripFrom = 0
            self.pixelNum = 144
            
        # Values for LedStrip 2
        # 166 Leds - after 144 Leds  
        elif self.LedStrip == 2:

            # Number of Pixels the Strip haves
            self.stripTo = 310
            self.stripFrom = 144
            self.pixelNum = 166
        
        self.cs = CHECKSTOP(self.V)
        self.db = DATABASE(self, self.V)
        
        # Declaration of strip
        self.pixels = neopixel.NeoPixel(board.D18, self.pixelCount, auto_write=False)
        
        self.firstShow()
    
        # verbose print and verbose creation of Objects
        if self.V:
            print("Initializing class STRIP")

            
    # Method autochange()
    # Autochanges between diffrent Lighting
    def autochange(self):
        
        mood = self.db.mood
        
        # verbose print
        if self.V:
            print("started STRIP.autochange()")
        
        
        while self.cs.checkstop:
            
            if mood == 0:
                r1 = round(random.random() * 255)
                g1 = round(random.random() * 255)
                b1 = round(random.random() * 255)

                r2 = round(random.random() * 255)
                g2 = round(random.random() * 255)
                b2 = round(random.random() * 255)

                zero = round(random.random() * 2)
                if zero == 0:
                    r1 = 0
                elif zero == 1:
                    g1 = 0
                elif zero == 2:
                    b1 = 0

                zero = round(random.random())

                if r1 == 0:
                    if zero == 0:
                        g2 = 0
                    elif zero == 1:
                        b2 = 0
                elif g1 == 0:
                    if zero == 0:
                        r2 = 0
                    elif zero == 1:
                        b2 = 0
                elif b1 == 0:
                    if zero == 0:
                        r2 = 0
                    elif zero == 1:
                        g2 = 0
                        
            elif mood == 1:
                r1 = 255
                g1 = round(random.random() * 50) * round(random.random())
                b1 = round(random.random() * 50) * round(random.random())

                r2 = 255
                g2 = round(random.random() * 50) * round(random.random())
                b2 = round(random.random() * 50) * round(random.random())

            
            self.gradient(r1, g1, b1, r2, g2, b2)

            self.cs.sleep(self.db.delay)
    
        self.db.updateCheckstop(1)
        
        # verbose print
        if self.V:
            print("stopped STRIP.autochange()")
        
    
    # Method clear()
    # sets pixels to black: 0, 0, 0
    def clear(self):
        
        for i in range(self.pixelNum):
            self.pixels[self.stripFrom + i] = (0, 0, 0)
            
        self.pixels.show()
        
        # verbose print
        if self.V:
            print("executed STRIP.clear(): (0, 0, 0)")
        
        # Updating db to new values
        self.db.updateStrip(self.pixels)
        
    # Method gradient() | gradient(r1, g1, b1, r2, g2, b2)
    # fading into another Gradient
    def gradient( self, r1=None, g1=None, b1=None, r2=None, g2=None, b2=None ):
        
        # Starts measurement of time
        s = time.time()

        # Checks if no attribute is given
        if ( r1 == None ):
            
            # setting attributes to Values of Database
            r1 = self.db.gradient1
            g1 = self.db.gradient2
            b1 = self.db.gradient3
            r2 = self.db.gradient4
            g2 = self.db.gradient5
            b2 = self.db.gradient6
        
        # Checks if one attribute is given
        elif ( g1 == None ):
            
            g1 = r1
            b1 = r1
            r2 = r1
            g2 = r1
            b2 = r1
            
        # Checks if two attributes are given
        elif ( b1 == None ):
            
            r2 = g1
            g2 = g1
            b2 = g1
            g1 = r1
            b1 = r1
            
        # Checks if three attributes are given
        elif ( r2 == None ):
            
            r2 = r1
            g2 = g1
            b2 = b1
            
        # Checks if four attributes are given
        elif ( g2 == None ):
            
            g2 = 0
            b2 = 0
            
        # Checks if five attributes are given
        elif ( b2 == None ):
            
            b2 = 0

        
        if self.cs.checkstop:

            # Declaration of Arrays
            r = []
            g = []
            b = []

            for i in range(self.pixelNum):
                if self.cs.checkstop:
                    if(r1 > r2 or r1 < r2):
                        r.append( round(r1 - (((r1-r2)/self.pixelNum) * i)))
                    elif(r1 == r2):
                        r.append(round(r1))

                    if(g1 > g2 or g1 < g2):
                        g.append( round(g1 - (((g1-g2)/self.pixelNum) * i)))
                    elif(g1 == g2):
                        g.append(round(g1))

                    if(b1 > b2 or b1 < b2):
                        b.append( round(b1 - (((b1-b2)/self.pixelNum) * i)))
                    elif(b1 == b2):
                        b.append(round(b1))

            # Checks transitiontype from database
            if self.db.transitiontype == 0:
                
                # Steps
                x = 10000

                # Repeating Steps
                for j in range(1, x + 1):

                    if self.cs.checkstop:

                        # Checking if passed time matches the expected time from database table preferences
                        if((time.time() - s < (float(self.db.transitionspeed) / x ) * j) or (j == x)):

                            # Repeating for every Pixel
                            for i in range(self.pixelNum):

                                self.pixels[self.stripFrom + i] = ( round(self.db.r[i] - (((self.db.r[i] - r[i])/x) * j)), round(self.db.g[i] - (((self.db.g[i] - g[i])/x) * j)), round(self.db.b[i] - (((self.db.b[i] - b[i])/x) * j)) )

                            # sending data to ledstrip
                            self.pixels.show()           
            elif self.db.transitiontype == 1:
                
                # Setting every Pixel to Value from Database
                for i in range(self.pixelNum):
                    
                    self.pixels[self.stripFrom + i] = (self.db.r[i], self.db.g[i], self.db.b[i])
                    
                # sending data to ledstrip
                self.pixels.show()

                # Repeating Steps
                for i in range(self.pixelNum):
                    
                    if self.cs.checkstop:

                        self.pixels[self.stripFrom + i] = (r[i], g[i], b[i])

                        # TODO: Not Correct time!!!
                        sleeptime = (((self.db.transitionspeed / self.pixelNum) * (i + 1)) - (time.time() - s))
                        
                        if sleeptime > 0 or self.pixelNum == i:
                            time.sleep(sleeptime)
                            
                            # sending data to ledstrip
                            self.pixels.show()
        else:
            print("Checkstop is at State 0")
            
            
        # Updating db to new values
        self.db.updateStrip(self.pixels)
        
        # verbose print
        if self.V:

            # Stops measurement of time
            t = str(round(time.time() - s, 3 ))

            if not self.cs.checkstop:
                print("terminated STRIP.gradient(): (" + str(r1) + ", " + str(g1) + ", " + str(b1) + ") --> (" + str(r2) + ", " + str(g2) + ", " + str(b2) + ") (after: " + t + "s)")

            else:
                print("executed STRIP.gradient(): (" + str(r1) + ", " + str(g1) + ", " + str(b1) + ") --> (" + str(r2) + ", " + str(g2) + ", " + str(b2) + ") (took: " + t + "s)")

                
    # Method firstShow()
    # fading into first Color
    def firstShow( self ):
        
        for i in range(self.pixelCount):
            self.pixels[i] = (self.db.rFull[i], self.db.gFull[i], self.db.bFull[i])
                
        self.pixels.show() 
            
                
    # Method color() | color(r, g, b)
    # fading into another Color
    def color( self, r=None, g=None, b=None ):
        
        # Checks if no attribute is given
        if ( r == None ):
            
            # setting attributes to Values of Database
            r = self.db.gradient1
            g = self.db.gradient2
            b = self.db.gradient3
            
        # Checks if only one attribute is given
        elif ( g == None ):
            
            # Setting other attributes to the given one
            g = r
            b = r
        
        # Checks if two attributes are given 
        elif ( b == None ):
            
            b = 0
        
        self.gradient(r, g, b)
    
    
    # Method blink()
    # Blinking Strip
    def blink(self):
        
        # verbose print
        if self.V:
            print("started STRIP.blink()")
        
        
        while self.cs.checkstop:
            
            self.gradient()

            self.cs.sleep(self.db.delay)
            
            self.gradient(0)
            
            self.cs.sleep(self.db.blinkspeed)
    
        self.db.updateCheckstop(1)
        
        # verbose print
        if self.V:
            print("stopped STRIP.blink()")
            
            
    # Method rainbow()
    # Fade to Rainbow Color Cycle
    def rainbow(self):
        
        # verbose print
        if self.V:
            print("started STRIP.rainbow()")
            
        self.firstShow()
        
        while self.cs.checkstop:
            
            for j in range(255):
                if self.cs.checkstop:
                    for i in range(self.stripFrom, self.stripTo):
                        if self.cs.checkstop:
                            pixel_index = (i * 256 // self.pixelCount) + j
                            self.pixels[i] = self.rainbowWheel(pixel_index & 255)
                    self.pixels.show()
                
        # Updating db to new values
        self.db.updateStrip(self.pixels)
    
        self.db.updateCheckstop(1)
        
        # verbose print
        if self.V:
            print("stopped STRIP.rainbow()")
    
    # Method rainbowWheel()
    # Gives Parameters for the Rainbow
    def rainbowWheel(self, pos):
        
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (r, g, b)
    
    
    # Method turnON()
    # reads the Database and setting the LEDs
    def turnON(self):
        
        if self.cs.checkstop:
            
            self.db.updatePower(1)
            
            if self.db.profile == 0:
                self.color()
            elif self.db.profile == 1:
                self.gradient()
            elif self.db.profile == 2:
                self.autochange()
            elif self.db.profile == 3:
                self.blink()
            elif self.db.profile == 4:
                self.rainbow()
            
            self.terminate()
        
    
    # Method turnOFF()
    # setting the LEDs and the Database to 0
    def turnOFF(self):
        
        self.color(0,0,0)
        
        self.db.updatePower(0)
        
        self.terminate()
        
    
    # Method terminate()
    # terminates Threads and the Strip itself
    def terminate(self):
        
        self.db.updateCheckstop(1)
        
        self.cs.terminate()
        self.db.terminate()
        
        if self.V:
            print("terminated Strip")
        
