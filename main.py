# main.py
import pygame
import sys
from ui import Button
from components import Resistor, Wire

# Define screen dimensions
WIDTH, HEIGHT = 800, 600

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)  # Highlight color for selected component or wire

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Simulator")

# Initialize font after Pygame has been initialized
FONT = pygame.font.SysFont("Arial", 16)

# Function to add a component to the scene
def add_component():
    # Add a new resistor component to the list
    components.append(Resistor((WIDTH // 2, HEIGHT // 2), 100))  # Add resistor at the center

def main():
    global components
    components = []  # List to store components (resistors, capacitors, etc.)
    wires = []  # List to store wires being drawn
    dragging_component = None  # Variable to keep track of the component being dragged
    current_wire = None  # To track the current wire being drawn
    wire_direction = None  # To track the direction of the wire (horizontal or vertical)
    selected_component = None  # To track the selected component for deletion
    selected_wire = None  # To track the selected wire for deletion

    # Create the button to add a component (resistor in this case)
    add_component_button = Button("Add Resistor", (WIDTH // 2 - 75, HEIGHT - 50), 150, 40, add_component)

    # Main game loop
    running = True
    while running:
        screen.fill(WHITE)  # Fill the screen with white

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if a component is clicked and start dragging or rotating
                for component in components:
                    if component.check_collision(event.pos):
                        # If already selected, deselect it
                        if selected_component == component:
                            selected_component = None
                        else:
                            selected_component = component  # Set the selected component
                        # Start dragging the component (resistor)
                        dragging_component = component
                        component.is_dragging = True
                        break

                # Check if a wire is clicked
                for wire in wires:
                    if wire.check_collision(event.pos):
                        # If already selected, deselect it
                        if selected_wire == wire:
                            selected_wire = None
                        else:
                            selected_wire = wire  # Set the selected wire
                        break

                # Check if clicking on a connection point to start a wire
                if not dragging_component and not selected_wire:
                    for component in components:
                        connection_points = component.get_connection_points()
                        for point in connection_points:
                            if pygame.Rect(point[0] - 5, point[1] - 5, 10, 10).collidepoint(event.pos):
                                current_wire = Wire(point, point)
                                wires.append(current_wire)  # Add wire to the list
                                wire_direction = None  # Reset the direction before determining it
                                break

                # If the "Add Resistor" button is clicked
                if add_component_button.is_hovered(event.pos):
                    add_component_button.click()

            if event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging the component and finalize the wire
                if dragging_component:
                    dragging_component.is_dragging = False
                    dragging_component = None  # Clear the dragging component once dropped

                if current_wire:
                    current_wire = None  # Reset the current wire after placement
                    wire_direction = None  # Reset wire direction when placement is complete

            if event.type == pygame.MOUSEMOTION:
                # Move the dragged component or update the wire's endpoint
                if dragging_component and dragging_component.is_dragging:
                    dragging_component.position = event.pos

                if current_wire:
                    # If no direction has been determined yet, find it
                    if wire_direction is None:
                        # Check if the wire is moving more horizontally or vertically
                        if abs(event.pos[0] - current_wire.start[0]) > abs(event.pos[1] - current_wire.start[1]):
                            wire_direction = 'horizontal'  # Horizontal movement
                        else:
                            wire_direction = 'vertical'  # Vertical movement

                    # Update the endpoint based on the determined direction
                    if wire_direction == 'horizontal':
                        current_wire.set_end((event.pos[0], current_wire.start[1]))  # Keep Y fixed
                    elif wire_direction == 'vertical':
                        current_wire.set_end((current_wire.start[0], event.pos[1]))  # Keep X fixed

            if event.type == pygame.KEYDOWN:
                # Rotate component by 90 degrees when 'r' is pressed
                if dragging_component and event.key == pygame.K_r:
                    dragging_component.rotate()
                
                # Delete the selected component when 'DELETE' key is pressed
                if event.key == pygame.K_DELETE:
                    if selected_component:
                        components.remove(selected_component)  # Remove the selected component
                        selected_component = None  # Clear the selection after deletion
                    if selected_wire:
                        wires.remove(selected_wire)  # Remove the selected wire
                        selected_wire = None  # Clear the selection after deletion

        # Draw the button (pass FONT to the draw method)
        add_component_button.draw(screen, FONT)

        # Draw all the components
        for component in components:
            component.draw(screen)

        # Highlight the selected component for deletion
        if selected_component:
            x, y = selected_component.position
            width, height = selected_component.width, selected_component.height  # Use width and height here
            pygame.draw.rect(screen, RED, (x - width // 2, y - height // 2, width, height), 2)

        # Draw the selected wire in a different color
        if selected_wire:
            selected_wire.draw(screen, highlight=True)  # Draw with highlighting for the selected wire

        # Draw all the wires
        for wire in wires:
            if wire != selected_wire:  # Don't draw the selected wire twice
                wire.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
