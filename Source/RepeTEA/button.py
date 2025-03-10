from config import * 

class Button: 
    def __init__(self, size, pos, color, label, font = stadart_font):
        self.heigth, self.width = size
        self.x, self.y = pos
        self.color = color
        self.text = font.render(label, True, TESTE2)

    def draw(self, screen): 
        textx, texty= self.text.get_size()

        pygame.draw.rect(screen, self.color, ((self.x - self.width/2, self.y - self.heigth/2) , (self.width, self.heigth)), 0, 10); 
        screen.blit(self.text, (self.x - textx/2, self.y - texty/2))


        

        