import pygame 

# Button class to create interactive buttons
class Button:
    def __init__(self, text, position, width, height, action=None):
        self.text = text
        self.position = position
        self.width = width
        self.height = height
        self.action = action

    def draw(self, screen, font):
        pygame.draw.rect(screen, (0, 255, 0), (self.position[0], self.position[1], self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (self.position[0], self.position[1], self.width, self.height), 2)
        text_surface = font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.position[0] + (self.width - text_surface.get_width()) // 2,
                                   self.position[1] + (self.height - text_surface.get_height()) // 2))

    def is_hovered(self, mouse_pos):
        """Check if mouse is hovering over the button"""
        return (self.position[0] <= mouse_pos[0] <= self.position[0] + self.width) and \
               (self.position[1] <= mouse_pos[1] <= self.position[1] + self.height)

    def click(self):
        if self.action:
            self.action()
