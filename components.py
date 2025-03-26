import pygame
import math

pygame.font.init()  # Ensure the font system is initialized

# Define constants for colors and font
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FONT = pygame.font.SysFont("Arial", 16)

# Base Component Class
class Component:
    def __init__(self, position, size):
        self.position = position  # Position of the component (centered)
        self.size = size  # Size (width, height) or other attributes
        self.angle = 0  # Rotation angle in degrees
        self.is_dragging = False

    def draw(self, screen):
        pass  # Should be implemented by subclasses

    def check_collision(self, mouse_pos):
        """Generalized collision check for rectangular bounding box."""
        x, y = self.position
        width, height = self.size
        # Creating a bounding box for collision detection
        bounding_box = pygame.Rect(x - width // 2, y - height // 2, width, height)
        return bounding_box.collidepoint(mouse_pos)
        
    def rotate(self):
        """Rotate the component by 90 degrees."""
        self.angle += 90
        if self.angle == 360:
            self.angle = 0  # Reset to 0 if it exceeds 360 degrees

class Resistor(Component):
    def __init__(self, position, resistance):
        self.resistance = resistance
        self.width = 60  # Set width first
        self.height = 20  # Set height first
        size = (self.width, self.height)  # Now create the size tuple using width and height
        super().__init__(position, size)  # Pass size to the parent class


    def draw(self, screen):
        x, y = self.position
        zigzag_width = self.size[0] - 10  # Reduced width for zigzag pattern
        zigzag_height = self.size[1] // 2  # Zigzag "height"
        num_zigzags = 8  # Number of zigzags

        # Create a surface to hold the rotated zigzag pattern
        resistor_surface = pygame.Surface((zigzag_width, self.size[1]), pygame.SRCALPHA)  # Create an alpha surface

        # Draw the zigzag resistor pattern
        for i in range(num_zigzags):
            start_x = i * zigzag_width // num_zigzags
            start_y = zigzag_height if i % 2 == 0 else -zigzag_height
            end_x = (i + 1) * zigzag_width // num_zigzags
            end_y = zigzag_height if (i + 1) % 2 == 0 else -zigzag_height
            pygame.draw.line(resistor_surface, BLACK, (start_x, start_y + self.size[1] // 2),
                             (end_x, end_y + self.size[1] // 2), 4)

        # Rotate the resistor surface by the current angle
        rotated_resistor = pygame.transform.rotate(resistor_surface, self.angle)
        new_rect = rotated_resistor.get_rect(center=(x, y))  # Center the rotated image

        # Draw the rotated resistor pattern on the main screen
        screen.blit(rotated_resistor, new_rect.topleft)

        # Draw the resistance value near the resistor
        text = FONT.render(f"{self.resistance}Ω", True, BLACK)
        screen.blit(text, (x - text.get_width() // 2, y - self.size[1] // 2 - 20))  # Position the text above the resistor

        # Draw connection points (at the ends of the resistor)
        self.connection_points = self.get_connection_points()
        for point in self.connection_points:
            pygame.draw.circle(screen, BLACK, point, 3)  # Draw a small circle at each connection point

    def get_connection_points(self):
        """Calculate the two connection points at the ends of the resistor."""
        x, y = self.position
        half_width = self.size[0] // 2
        angle_rad = math.radians(self.angle)  # Convert angle to radians

        # Calculate the offset for both ends of the resistor
        x_offset = half_width * math.cos(angle_rad)
        y_offset = half_width * math.sin(angle_rad)

        # Connection points are in the middle of the resistor (no change)
        left_end = (x - x_offset, y - y_offset)
        right_end = (x + x_offset, y + y_offset)

        return [left_end, right_end]

# Battery Component Class
class Battery(Component):
    def __init__(self, voltage, position):
        super().__init__(position, (30, 40))  # Size of the battery
        self.voltage = voltage

    def draw(self, screen):
        x, y = self.position
        width, height = self.size
        # Draw the battery
        pygame.draw.rect(screen, BLUE, (x - width // 2, y - height // 2, width, height), 2)
        pygame.draw.line(screen, BLUE, (x, y - height // 2), (x, y + height // 2), 3)

        # Draw voltage label
        text = FONT.render(f"{self.voltage}V", True, BLACK)
        screen.blit(text, (x - text.get_width() // 2, y + height // 2 + 5))

# This is the class where we define everything for wires
class Wire:
    def __init__(self, start, end):
        self.start = start  # Start position of the wire (tuple)
        self.end = end      # End position of the wire (tuple)

    def draw(self, screen, highlight=False):
        color = RED if highlight else BLACK  # Highlight selected wires in red
        pygame.draw.line(screen, color, self.start, self.end, 2)

    def set_end(self, end):
        # Update the end position of the wire (useful while dragging)
        self.end = end

    def check_collision(self, mouse_pos):
        """Check if the mouse is near the wire (line segment)."""
        # Create vector representations of the wire's start and end points
        line_start = pygame.math.Vector2(self.start)
        line_end = pygame.math.Vector2(self.end)
        mouse_pos = pygame.math.Vector2(mouse_pos)

        # The line length
        line_length = line_start.distance_to(line_end)

        # The distance from the mouse position to the line
        # This function calculates the perpendicular distance from the mouse point to the line segment
        distance = line_start.distance_to(mouse_pos) + line_end.distance_to(mouse_pos) - line_length

        # If the distance is small enough, consider it a "collision"
        return abs(distance) < 5  # This threshold (5) is the buffer zone, similar to tolerance


# Probe Component Class
class Probe(Component):
    def __init__(self, position):
        super().__init__(position, (10, 10))  # Probe size (circle radius)
    
    def draw(self, screen):
        x, y = self.position
        pygame.draw.circle(screen, RED, self.position, 5)
