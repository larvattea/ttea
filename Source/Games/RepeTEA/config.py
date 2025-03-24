import pygame

pygame.font.init()
pygame.init() 

# Para a proporção padrão de 16:9, codifique com estas resoluções:
#     4320p (8K): 7680 x 4320
#     2160p (4K): 3840 x 2160
#     1440p (2K): 2560 x 1440
#     1080p (HD): 1920 x 1080
#     720p (HD): 1280 x 720
#     480p (SD): 854 x 480
#     360p (SD): 640 x 360
#     240p (SD): 426 x 240

WIDHT = 800
HEIGHT = 600

#Frames per Seconds
FPS = 60


#Font 



#Colors
BLUE = (0,0, 255)
RED  = (255,0,0)
GREEN = (0,255,0)
YELLOW =  (255,255,0)
WHITE = (255,255,255)
BLACK  = (0,0,0)
TESTE = (252, 163, 17)
TESTE2 = (229, 229, 229)

#Font

stadart_font =  pygame.font.SysFont("Serif", int(HEIGHT * 0.05))


#Images 
repetea_logo =  pygame.image.load(r"Source\Assets\Repetea_Figuras\repetea_logo.png")
# emoji_feliz = pygame.image.load("Source\Assets\Repetea_Figuras\feliz2.png")
# emoji_triste = pygame.image.load("Source\Assets\Repetea_Figuras\triste2.png")


#Sounds: 
# som_acerto = mixer.Sound(r"Source\Assets\Repetea_Sons\padrao\5_feliz.wav")
# som_erro  = pygame.mixer.Sound ("Source\Assets\Repetea_Sons\padrao\6_triste.wav")
# som_ajuda = pygame.mixer.Sound ("Source\Assets\Repetea_Sons\padrao\11_ajuda.wav")
# som_base  = pygame.mixer.Sound (" ")


