# KarTEA.py
import pygame


class KarTEA:
    """Classe principal que gerencia o jogo KarTEA (menu + game loop)"""

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))

        self.clock = pygame.time.Clock()

        # Controle de saída
        self.running = True

    def run(self):
        """Loop principal do jogo"""
        while self.running:
            # Process player inputs.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            self.screen.fill("purple")  # Fill the display with a solid color

            pygame.display.flip()  # Refresh on-screen display
            self.clock.tick(60)


# Ponto de entrada padrão
if __name__ == "__main__":
    game = KarTEA()
    game.run()
