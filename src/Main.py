import pygame
import sys

class Wire:
    def __init__(self, start_pos, end_pos, isTemporary):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = (100,100,100) if isTemporary else (0,0,0)
        self.isTemporary = isTemporary

    def isTemporary(self):
        return self.isTemporary
    
    def makePermanent(self):
        self.isTemporary = False
        self.color = (0,0,0)

    def change_end_point(self,new_pos):
        self.end_pos = new_pos

    def translate(self, displacement):
        self.start_pos = (self.start_pos[0] + displacement[0], self.start_pos[1] + displacement[1])
        self.end_pos = (self.end_pos[0] + displacement[0], self.end_pos[1] + displacement[1])

    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, 8)


class Node:
    another_selected = False
    selected_wire = None
    selected_node = None
    total_nodes = 0#A list of the indicies of nodes
                    #Status of the visited nodes during the dfs
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = (255, 0, 0)  # Red color by default
        self.wires = []#Only the last wire is a temporary wire
        self.selected = False
        self.number = Node.total_nodes
        self.event_handled = False
        Node.total_nodes += 1

    def cycle_over(self):
        self.event_handled = False
        for _,node in self.wires:
            if node is not None and node.number > self.number:
                node.cycle_over()

    def draw(self, surface):
        for wire,node in self.wires:
            if node is None:
                wire.draw(surface)
            elif node.number > self.number:
                wire.draw(surface) #If cond is not satisfied, the other node will draw it
                node.draw(surface)

        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius) #Drawing self
        if self.selected:
            pygame.draw.circle(surface, (0, 255, 0), (self.x, self.y), self.radius + 2, 2)
    
 
    def handle_event(self, event,displacement):
        if self.event_handled == True:
            return None
        self.event_handled = True
        #Translation handle
        self.x += displacement[0]
        self.y += displacement[1]

        #Event handle
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius).collidepoint(event.pos):
                if(self.selected == False):#Previous value
                    if(Node.another_selected == False):
                        #I need to add a temporary Wire
                        self.wires.append((Wire((self.x,self.y), pygame.mouse.get_pos(), True), None))
                        self.selected = True

                        #Changing global variables
                        Node.another_selected = True
                        Node.selected_wire = self.wires[-1][0]
                        Node.selected_node = self
                    else: #User wants to connect a wire between the nodes
                        #It is your responsibility to transfer the info to the node that it not need to be selected anymore
                        self.wires.append((Node.selected_wire, Node.selected_node))
                        Node.selected_wire.makePermanent()

                        #Updating the other nodes values
                        #Node.selected_node.wires.pop() #It is self's wire now
                        Node.selected_node.wires[-1] = (Node.selected_wire, self)
                        Node.selected_node.selected = False

                        #Changing the static variables
                        Node.another_selected = False
                        Node.selected_node = None
                        Node.selected_wire = None

                else:
                    #I need to remove the temporary wire
                    self.wires.pop()
                    self.selected = False

                    Node.another_selected = False
                    Node.selected_node = None
                    Node.selected_wire = None

        if self.selected:
            self.wires[-1][0].change_end_point(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.selected = False
                node = Node(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
                self.wires[-1][0].makePermanent()
                self.wires[-1] = (self.wires[-1][0], node)
                node.wires.append((self.wires[-1][0], self))

                #Changing the global variables
                Node.another_selected = False
                Node.selected_node = None
                Node.selected_wire = None
        
        for wire,node in self.wires:
            if node is None:
                wire.translate(displacement)
            elif node.number > self.number:
                wire.translate(displacement)
                node.handle_event(event, displacement)
            
    
class Battery:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.offset = (0, 0)
        self.nodes = [Node(self.rect.left, self.rect.centery), Node(self.rect.right, self.rect.centery)]
        self.voltage = 5 # Default voltage
        self.voltage_rect = pygame.Rect(0, 0, 0, 0)  # Initialize voltage_rect
        self.editing = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        font = pygame.font.Font(None, 80)
        voltage_text = font.render(f"{self.voltage} V", True, (0, 0, 0))
        self.voltage_rect = voltage_text.get_rect(center=(self.rect.centerx, self.rect.y - 20))
        surface.blit(voltage_text, self.voltage_rect)
        if self.editing:
            pygame.draw.rect(surface, (255, 255, 0), self.voltage_rect, 2)



        # Draw nodes
        for node in self.nodes:
            node.draw(surface)
        if self.editing:
            pygame.draw.rect(surface, (255, 255, 0), self.voltage_rect, 2)

    def handle_event(self, event):
        self.nodes[0].handle_event(event, (self.rect.left - self.nodes[0].x, self.rect.centery - self.nodes[0].y))
        self.nodes[1].handle_event(event, (self.rect.right - self.nodes[1].x, self.rect.centery - self.nodes[1].y))
        for i in self.nodes:
            i.cycle_over()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.offset = (self.rect.x - event.pos[0], self.rect.y - event.pos[1])
            if event.button == 3: #Right mouse button means editing
                if self.voltage_rect.collidepoint(event.pos):
                    self.editing = not self.editing

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset[0]
                self.rect.y = event.pos[1] + self.offset[1]
        #TODO: Handle double inputs
        elif event.type == pygame.KEYDOWN and self.editing:
            if event.key == pygame.K_RETURN:#An enter is a perfectly valid way of ending the editing cycle
                self.editing = False
            elif event.key == pygame.K_BACKSPACE:
                self.voltage = self.voltage // 10
            elif pygame.K_0 <= event.key <= pygame.K_9:
                self.voltage = self.voltage * 10 + int(pygame.key.name(event.key))
    

# Create Battery object
battery = Battery(100, 100, 'rsc/battery.png')  # x, y, image_path
# Initialize Pygame
pygame.init()

# Set up display
width, height = 1600, 1200
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("My Pygame")

# Set up game loop variables
clock = pygame.time.Clock()
running = True

# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            battery.handle_event(event)
    # Draw on the screen
    screen.fill((255, 255, 255))  # Fill screen with white color
    battery.draw(screen)
    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()