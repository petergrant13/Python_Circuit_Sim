# ui.py
import pygame
import sys
from components import Resistor  # Importing the Resistor class from components.py

# Define screen dimensions
WIDTH, HEIGHT = 800, 600

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Simulator")

# Font for text
FONT = pygame.font.SysFont("Arial", 16)

# Button class to create interactive buttons
class Button:
    def __init__(self, text, position, width, height, action=None):
        self.text = text
        self.position = position
        self.width = width
        self.height = height
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.position[0], self.position[1], self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.position[0], self.position[1], self.width, self.height), 2)
        text_surface = FONT.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.position[0] + (self.width - text_surface.get_width()) // 2,
                                   self.position[1] + (self.height - text_surface.get_height()) // 2))

    def is_hovered(self, mouse_pos):
        # Check if mouse is hovering over the button
        return (self.position[0] <= mouse_pos[0] <= self.position[0] + self.width) and \
               (self.position[1] <= mouse_pos[1] <= self.position[1] + self.height)

    def click(self):
        if self.action:
            self.action()

# Function to add a resistor to the scene
def add_resistor():
    # Add a new resistor to the list, instead of replacing the existing one
    resistors.append(Resistor((WIDTH // 2, HEIGHT // 2), 100))  # Add resistor at the center of the screen

# Main function
def main():
    global resistors
    resistors = []  # List to store resistors
    dragging_resistor = None  # Variable to keep track of the resistor being dragged

    # Create the button to add a resistor
    add_resistor_button = Button("Add Resistor", (WIDTH // 2 - 75, HEIGHT - 50), 150, 40, add_resistor)

    # Main game loop
    running = True
    while running:
        screen.fill(WHITE)  # Fill the screen with white

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any resistor is clicked and start dragging
                for resistor in resistors:
                    if resistor.check_collision(event.pos):
                        dragging_resistor = resistor  # Set the resistor that is being dragged
                        dragging_resistor.is_dragging = True
                        break

                # If the "Add Resistor" button is clicked
                if add_resistor_button.is_hovered(event.pos):
                    add_resistor_button.click()

            if event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging the current resistor
                if dragging_resistor:
                    dragging_resistor.is_dragging = False
                    dragging_resistor = None  # Clear the dragging resistor once dropped

            if event.type == pygame.KEYDOWN:
                # Rotate resistor by 90 degrees when 'r' is pressed
                if dragging_resistor and event.key == pygame.K_r:
                    dragging_resistor.angle += 90
                    if dragging_resistor.angle == 360:
                        dragging_resistor.angle = 0

            if event.type == pygame.MOUSEMOTION:
                # Move the dragged resistor
                if dragging_resistor and dragging_resistor.is_dragging:
                    dragging_resistor.position = event.pos

        # Draw the button
        add_resistor_button.draw(screen)

        # Draw all the resistors
        for resistor in resistors:
            resistor.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()