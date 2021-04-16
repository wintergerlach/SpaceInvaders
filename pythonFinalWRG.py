import random
from livewires import games, color

games.init(screen_width = 640, screen_height = 540, fps = 50)

#the noise
games.music.load("background.mp3")
explosionSound = games.load_sound("explosion.wav")
laserSound = games.load_sound("missile.wav")

#all the code to make a ship
class Ship(games.Sprite):
    #ship image
    image = games.load_image("ship.png")
    #how long between lasers
    LASER_TIME = 75
    currentScore = 0
    lives = 3
    gameOver = False
    win = False
    hit = 20
    #score text
    score = games.Text(value = 0, size = 30, color = color.purple,
                top = 5, left = 25)
    games.screen.add(score)

    #create ship and lives
    def __init__(self, x, y):
        super(Ship, self).__init__(image=Ship.image, x=x, y=y)
        self.laser_wait = 0
        self.livesShow = games.Text(value = 3 , size = 30, color = color.purple,
                top = 5, right = games.screen.width - 10)
        games.screen.add(self.livesShow)

    #controls ship movement
    def update(self):
        if Ship.gameOver == False:
            super(Ship, self).update
            if games.keyboard.is_pressed(games.K_LEFT):
                if self.left != 0:
                    self.x -= 1       
            if games.keyboard.is_pressed(games.K_RIGHT):
                if self.right != games.screen.width:
                    self.x += 1

            if self.laser_wait >0:
                self.laser_wait -=1

            #shoots a laser   
            if games.keyboard.is_pressed(games.K_SPACE) and self.laser_wait ==0:
                laserSound.play()
                new_laser = Laser(self.x, self.y, sender="ship")
                games.screen.add(new_laser)
                self.laser_wait = Ship.LASER_TIME
            
            #handles if the sprite touches another sprite
            if self.overlapping_sprites:
                for sprite in self.overlapping_sprites:
                    sprite.die()
                self.die
        
        #prints a win message if all ships are hit
        if Ship.win == True:
            win_game = games.Message(value = "You Win",
                                     size = 90,
                                     color = color.green,
                                     x = games.screen.width/2,
                                     y = games.screen.height/2,
                                     lifetime = 5* games.screen.fps,
                                     after_death = games.screen.quit)
            games.screen.add(win_game)

    #ship death
    def die(self):
        #game over
        if Ship.lives == 0:
            explosionSound.play()
            new_explosion = Explosion(x=self.x, y=self.y)
            games.screen.add(new_explosion)
            self.destroy()
            end_game = games.Message(value = "Game Over",
                                     size = 90,
                                     color = color.red,
                                     x = games.screen.width/2,
                                     y = games.screen.height/2,
                                     lifetime = 5* games.screen.fps,
                                     after_death = games.screen.quit)
            games.screen.add(end_game)
        #remove a life and create an explosion
        else:
            Ship.hit = 10
            Ship.lives -=1
            self.livesShow.value -=1
            explosionSound.play()
            new_explosion = Explosion(x=self.x, y=self.y)
            games.screen.add(new_explosion)
            self.destroy()
            if self.x < 40:
                self.x+=40
            else:
                self.x -= 40
            ship = Ship(x = self.x, y=500)
            games.screen.add(ship)

    
#all the code to make an alien
class Alien(games.Sprite):
    #alien array
    aliens=[]
    #move left on 0 right on 1
    direction = 0 
    #how many core aliens have been hit
    alienCount = 0
    #handles shooting countdowns and random alien creation countdowns
    shootCountdown = 2000
    randomChance = 0
    randomTime = 2000
    randomShooter = 0
    #alien images
    images = { 10: games.load_image("10pt.png"),
           20: games.load_image("20pt.png"),
           40: games.load_image("40pt.png"),
           80: games.load_image("randompt.png")
           }
    #create an alien
    def __init__(self, x, y, points, canShoot, spot):
        super(Alien, self).__init__(image = Alien.images[points], x=x, y=y)
        self.points = points
        self.canShoot = canShoot
        self.spot = spot

    # alien movement, creation and shooting
    def update(self):
        if Ship.gameOver == False:
            #create random alien
            Alien.randomChance = random.randint(1,10)
            if Alien.randomChance == 1 and Alien.randomTime == 0:
                new_alien = Alien(x=0, y=60, points = 80, canShoot = False, spot = 100)
                games.screen.add(new_alien)
                Alien.randomTime = 10000
                
            if Alien.randomChance != 1 and Alien.randomTime == 0:
                Alien.randomTime = 700
            
            #alien movement 
            if Alien.direction == 0 and self.points < 41:
                if self.left == 0:
                    Alien.direction = 1
                    for alien in Alien.aliens:
                        alien.y+=1
                else:
                    self.x -=0.25
            elif Alien.direction == 1 and self.points <41:
                if self.right == games.screen.width:
                    Alien.direction = 0
                    for alien in Alien.aliens:
                        alien.y+=1
                else:
                    self.x +=0.25
            else:
                self.x+=2

            #alien shooting  
            if Alien.shootCountdown == 0:
                Alien.randomShooter = random.randint(0, 59)
                for alien in Alien.aliens:
                    if alien.canShoot == True:
                        if alien.spot == Alien.randomShooter:
                            if alien.points < 80:
                                new_laser = Laser(self.x, self.y, sender="alien")
                                games.screen.add(new_laser)
                                Alien.shootCountdown = 5000

            #countdown for shooting and creation
            if Alien.shootCountdown >0:
                Alien.shootCountdown -=1
                
            if Alien.randomTime > 0:
                Alien.randomTime -=1
            
    #handles alien death
    def die(self):
        #when random dies picks points
        if self.points == 80:
            self.points = random.choice([50, 100, 150])
            Ship.currentScore += self.points
            Ship.score.value += self.points
        #sets the score
        else:
            Ship.currentScore += self.points
            Ship.score.value += self.points
            Alien.alienCount +=1

        #sets the canshoot variable  
        for alien in Alien.aliens:
            if alien.spot == self.spot - 10:
                alien.canShoot = True
        self.destroy()
        
        #checks for game over
        if Alien.alienCount == 60:
            Ship.win = True
            Ship.gameOver = True

#all the code needed to make a barrier   
class Barrier(games.Sprite):
    #all barrier images
    image = { 0: games.load_image("barrierFull.png"),
              1: games.load_image("barrier1.png"),
              2: games.load_image("barrier2.png"),
              3: games.load_image("barrier3.png")}

    #create the barrier
    def __init__(self, x, y, hit):
        super(Barrier, self).__init__(image = Barrier.image[hit], x = x, y = y)
        #set the initial number of hits
        self.hit = hit

    #what to do if a barrier is hit
    def die(self):
        #if it hasnt been hit 3 times yet
        if self.hit !=3:
            #make a new weaker barrier
            new_barrier = Barrier(x=self.x, y=self.y, hit = self.hit+1)
            games.screen.add(new_barrier)
            #destroy current barrier
            self.destroy()
        #hit 3 times then destroy it
        else:
            self.destroy()

#all the code for a laser
class Laser(games.Sprite):
    image = games.load_image("lazer.png")

    #create the laser
    def __init__(self, sender_x, sender_y, sender):
        #sets initial position and direction
        if sender == "ship":
            x = sender_x 
            y = sender_y-50
            dy = -1
        if sender == "alien":
            x=sender_x
            y=sender_y + 41
            dy = 1
        super(Laser, self).__init__(image = Laser.image,
                                    x = x,
                                    y = y,
                                    dy = dy)
        #sets sender variable 
        self.sender = sender

    #move the laser       
    def update(self):
        #destroy if it goes off the bottom of the screen
        if self.top >games.screen.height:
            self.die()
        #destory if it foes off the top of the screen
        if self.top < 0:
            self.die()

        #handles collisions
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                #if an alien hits an alien just destory laser 
                if type(sprite) is Alien and self.sender=="alien":
                    self.die()
                #if an alien laser hits ship or ship laser hits alien
                else:
                    #call the sprite death method then kill laser
                    sprite.die()
                    self.die()

    #destory the laser
    def die(self):
        self.destroy()

#all the code to make an explosion
class Explosion(games.Animation):
    #explosion images
    images = ["explosion1.png",
    "explosion2.png",
    "explosion3.png",
    "explosion4.png",
    "explosion5.png",
    "explosion6.png",
    "explosion7.png",
    "explosion8.png",
    "explosion9.png"]

    #create the explosion
    def __init__(self, x, y):
        super(Explosion, self).__init__(images = Explosion.images,
        x=x, y=y,
        repeat_interval=4, n_repeats = 1)

    #death function that just fixes the error if sprite.die is 
    #called on it 
    def die(self):
        print("")

#create the initial alien sprites
def createAliens():
    canShoot = False
    totalAliens = 0
    pointCounter = 0
    points = 10
    x = 75
    y = 240
    singleLineNumber = 0
    
    #while there are not 60 aliens keep making aliens
    while totalAliens < 60:
        #change points if this hits 20
        if pointCounter < 20: 
            #makes 10 aliens per line
            if singleLineNumber < 10: 
                new_alien = Alien(x=x, y=y, points = points, canShoot = totalAliens >49 and totalAliens < 60, spot=totalAliens)
                games.screen.add(new_alien)
                x+=50
                singleLineNumber+=1
                pointCounter+=1
                totalAliens+=1
                #add freshly created alien to the array
                Alien.aliens.append(new_alien) 
            #create a new row of aliens on the screen
            else: 
                x = 75
                y-=30
                singleLineNumber = 0
        #increase the point value of the aliens and create a new row of aliens
        else: 
            y-=30
            x = 75
            points*=2
            singleLineNumber = 0
            pointCounter = 0

#a function to create barriers
def createBarriers():
    x = 80
    y = 450
    totalBarriers = 0
    while totalBarriers < 4:
        new_barrier = Barrier(x=x, y=y, hit=0)
        games.screen.add(new_barrier)
        x+=150
        totalBarriers +=1
     
def main():
    #play music
    games.music.play(-1)
    #create background
    background_image = games.load_image("background.jpeg")
    games.screen.background = background_image
    #create and add sprites
    ship = Ship(x = games.screen.width/2, y=500)
    games.screen.add(ship)
    createAliens()
    createBarriers()
    #run
    games.screen.mainloop()

main()
