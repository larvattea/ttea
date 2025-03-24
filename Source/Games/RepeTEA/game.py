import pygame
from Jogador import Player
from config import * 
from geometry import *
from random import choices
from menu import * 

class Jogo: 
    def __init__(self, fase, nivel, screen):
        self.fase = fase 
        self.nivel = nivel
        self.player = Player(WHITE, WIDHT/30, (WIDHT/2, HEIGHT/2)) 
        self.root =  Root(HEIGHT/7, (WIDHT *0.5, HEIGHT *0.8))
        self.polygons = []
        self.screen = screen
        self.clock  = pygame.time.Clock()

    
    def set_polygons(self):
        circle = Circle(RED, HEIGHT/14, (WIDHT *0.6, HEIGHT * 0.2))
        square = Parallelogram(BLUE, HEIGHT/7, HEIGHT/7,  (WIDHT *0.8, HEIGHT * 0.4))
        triangle = Triangle(GREEN, HEIGHT/7,  (WIDHT *0.2, HEIGHT * 0.4))
        rectangle = Parallelogram(YELLOW, HEIGHT/5, HEIGHT/7, (WIDHT *0.4, HEIGHT * 0.2))
        self.polygons = [circle, square, triangle, rectangle]

    def draw_everything(self): 
        for i in self.polygons: 
            i.draw(self.screen)

        self.player.draw(self.screen) 
        self.root.draw(self.screen)

    def collision_polygon(self, obj_pos):
        for i in self.polygons: 
            if i.collide(obj_pos):
                return i
            
        return False

    def new_sequence(self):

        return choices(self.polygons, None, k=self.fase)


    def main_loop(self):

        self.set_polygons() 
        sequence = self.new_sequence()
        acertos = []
        erros = []
        aux = 0
        frames = 0
        time = 0
        state = 0
        run = True
        menu = Menu(repetea_logo)

        
    
        while run: 
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    run = False
                
            self.player.x, self.player.y = pygame.mouse.get_pos()
            self.screen.fill(BLACK)
            self.draw_everything()

            if state == -1: 
                menu.draw(self.screen)

            if state == 0:

                if time >= len(sequence) * 2 : 
                    state = 1
                else: 
                    if time%2 == 0: 
                        sequence[time//2].width = 0 
                    else: 
                        sequence[time - (time+1)//2].width = 3
                
            elif state == 1:               
                if self.root.collide(self.player.get_center()):
                   if not aux:  
                       aux = time

                   elif aux == time-2: 
                        self.root.add_circle()
                        aux-=1
                   
                   elif aux == time-5: 
                       self.root.add_circle()
                       state=2   
                    
                else:
                    self.root.remove_circles()
                    aux = None

            elif state == 2: 
                if self.root.collide(self.player.get_center()):
                    state = 3

            elif state == 3: 
                   
                polygon = self.collision_polygon(self.player.get_center())
                if polygon:  
                    rp = sequence.pop(0)
                    if polygon == rp: 
                        acertos.append(rp)
                    else: 
                        erros.append(rp)

                    state = 2

                if sequence == []: 
                    run = False    

            self.player.x, self.player.y = pygame.mouse.get_pos()


            frames+=1

            if frames % FPS == 0: 
                time+=1
                frames = 0
            
            self.clock.tick(60)
            pygame.display.flip()
           

            



                


            
        




    



        

        