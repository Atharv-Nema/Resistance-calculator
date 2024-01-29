import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WIRES = []

# Colors
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wire Drawing")

# Create clock object to control the frame rate
clock = pygame.time.Clock()

def draw_wire(start_pos, end_pos):
    pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)

def main():
    global WIRES

    drawing_wire = False
    current_wire = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing_wire = True
                current_wire = [event.pos]
            elif event.type == pygame.MOUSEMOTION:
                if drawing_wire:
                    current_wire.append(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing_wire = False
                WIRES.append(list(current_wire))

        screen.fill(TRANSPARENT)

        # Draw existing wires
        for wire in WIRES:
            if len(wire) > 1:
                for i in range(len(wire) - 1):
                    draw_wire(wire[i], wire[i + 1])

        # Draw current wire being drawn
        if drawing_wire and len(current_wire) > 1:
            draw_wire(current_wire[-2], current_wire[-1])

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
