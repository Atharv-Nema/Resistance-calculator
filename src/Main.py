import pygame
import sys
import math
import subprocess

class Wire:
    '''Represents a wire'''
    def __init__(self, start_pos, end_pos, is_temporary):
        '''Initializes the wire object'''
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = (100,100,100) if is_temporary else (0,0,0)
        self.is_temporary = is_temporary
        self.selected = False
        self.resistor_form = None # If the wire is transformed into a resistor, we store the reference of
        # the created resistance here for propogation of the transformation
        self.current = None

    def is_temporary(self):
        '''Returns whether the wire is temporary'''
        return self.is_temporary


    def get_resistance(self):
        return 0
    
    def make_permanent(self, start_node, end_node):
        '''Makes the wire permanent'''
        # start_node is associated with self.start_pos
        # end_node is associated with self.end_pos
        self.start_node: Node = start_node
        # assert self.start_pos == (start_node.x, start_node.y)
        # assert self.end_pos == (end_node.x, end_node.y)
        self.end_node: Node = end_node
        self.is_temporary = False
        self.color = (0,0,0)

    def change_end_point(self,new_pos):
        '''
        Changes the end position of the wire(for example, when the wire is temporary, we would be changing the
        end position to be that of the cursor location
        '''
        self.end_pos = new_pos

    def handle_event(self, event, displacement) -> bool:
        '''
        Handles and event and performs any necessary displacements
        '''
        #Displacement
        self.start_pos = (self.start_pos[0] + displacement[0], self.start_pos[1] + displacement[1])
        self.end_pos = (self.end_pos[0] + displacement[0], self.end_pos[1] + displacement[1])

        #Event handling
        mouse_pos = pygame.mouse.get_pos()
        THRESHOLD = 5 # 
        EPS = 0.05
        length = ((self.end_pos[1] - self.start_pos[1]) ** 2 + (self.end_pos[0] - self.start_pos[0]) ** 2) ** 0.5
        if event != None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            #Checking if click is on the line
            if(length == 0):
                distance_to_line = THRESHOLD + 1 # Do not perform a click as the wire has just been created
            else:
                new_end_pos = (self.end_pos[0] + EPS * (self.start_pos[0] - self.end_pos[0]), self.end_pos[1] + EPS * (self.start_pos[1] - self.end_pos[1]))
                new_start_pos = (self.start_pos[0] + EPS * (self.end_pos[0] - self.start_pos[0]), self.start_pos[1] + EPS * (self.end_pos[1] - self.start_pos[1]))
                d1_dot_line =  (mouse_pos[0] - new_start_pos[0]) * (new_end_pos[0] - new_start_pos[0]) + (mouse_pos[1] - new_start_pos[1]) * (new_end_pos[1] - new_start_pos[1])
                d2_dot_line = (mouse_pos[0] - new_end_pos[0]) * (new_start_pos[0] - new_end_pos[0]) + (mouse_pos[1] - new_end_pos[1]) * (new_start_pos[1] - new_end_pos[1])
                if d1_dot_line < 0 or d2_dot_line < 0:
                    distance_to_line = THRESHOLD + 2
                else:
                    #Calculate the distance normally
                    distance_to_line = abs(
                        (new_end_pos[1] - new_start_pos[1]) * pygame.mouse.get_pos()[0]
                        - (new_end_pos[0] - new_start_pos[0]) * pygame.mouse.get_pos()[1]
                        + new_end_pos[0] * new_start_pos[1]
                        - new_end_pos[1] * new_start_pos[0]
                        ) / length
            
            if distance_to_line < THRESHOLD:  # Adjust the threshold as needed
                self.selected = not self.selected
            else:
                self.selected = False

    def ingest_build_data(self, build_data):
        start_node_num = self.start_node.number
        end_node_num = self.end_node.number
        current_info = build_data['current_info']
        if start_node_num in current_info and end_node_num in current_info[start_node_num]:
            self.current = current_info[start_node_num][end_node_num]
        else:
            assert end_node_num in current_info and start_node_num in current_info[end_node_num]
            self.current = -current_info[end_node_num][start_node_num]

    def remove_build_data(self):
        self.current = None

    def is_transformation_request(self, event):
        '''Returns whether the event is intended to change the wire to a resistor'''
        if self.current is None and self.selected:
            if event != None and self.selected and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
        return False
    
    def draw_current(self, surface):
        # Drawing the current arrow and label
        if self.current is None:
            return
        
        arrow_color = (255, 0, 0)  # Red color for the arrow
        arrow_width = 3            # Width of the arrow line
        arrow_length = 20          # Length of the arrowhead lines

        # Determine direction based on the sign of the current
        if self.current < 0:
            start_pos = self.end_pos
            end_pos = self.start_pos
        else:
            start_pos = self.start_pos
            end_pos = self.end_pos

        # Draw the main line of the arrow
        pygame.draw.line(surface, arrow_color, self.start_pos, self.end_pos, arrow_width)

        # Calculate the midpoint of the line
        midpoint = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)

        # Calculate arrowhead direction
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx**2 + dy**2)

        if length != 0:
            unit_dx = dx / length
            unit_dy = dy / length

            # Points for the arrowhead lines at the midpoint
            arrow_point1 = (midpoint[0] - unit_dx * arrow_length + unit_dy * arrow_length,
                            midpoint[1] - unit_dy * arrow_length - unit_dx * arrow_length)
            arrow_point2 = (midpoint[0] - unit_dx * arrow_length - unit_dy * arrow_length,
                            midpoint[1] - unit_dy * arrow_length + unit_dx * arrow_length)

            if self.current != 0:
                # Draw the arrowhead at the midpoint
                pygame.draw.line(surface, arrow_color, midpoint, arrow_point1, arrow_width)
                pygame.draw.line(surface, arrow_color, midpoint, arrow_point2, arrow_width)

        # Draw the current value below the arrow
        font = pygame.font.Font(None, 24)
        current_text = font.render(f"{abs(self.current):.2f} A", True, (0, 255, 0))
        text_pos = (midpoint[0], midpoint[1] + 20)
        surface.blit(current_text, current_text.get_rect(center=text_pos))
            
    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, 8)
        self.draw_current(surface)
        if self.selected:
            pygame.draw.line(surface, (255, 255, 0), self.start_pos, self.end_pos, 16)



class Node:
    '''Class that represents the node'''
    another_selected = False
    temporary_wire = None
    selected_node = None
    total_nodes = 0#A list of the indicies of nodes
                    #Status of the visited nodes during the dfs
    def __init__(self, x, y):
        '''Initializes the Node object'''
        self.x = x
        self.y = y
        self.radius = 5
        self.color = (255, 0, 0)  # Red color by default
        self.wires: list[tuple[Wire, Node]] = [] #Precondition: If temporary wire exists, it is the last wire.
        self.selected = False
        self.number = Node.total_nodes
        self.event_handled = False
        self.voltage = None
        Node.total_nodes += 1

    def reset_event_handled(self):
        '''Sets self.event_handled to false for all nodes'''
        self.event_handled = False
        for _,node in self.wires:
            if node is not None and node.number > self.number:
                node.reset_event_handled()

    def draw(self, surface):
        '''
        Draws the node + wire on the surface, and sends the draw signal to other connected parts based on
        node number
        '''
        for wire,node in self.wires:
            if node is None:
                wire.draw(surface)
            elif node.number > self.number: 
                # Only purpose is to prevent an infinite loop(multiple draws do not not matter)
                wire.draw(surface) #If cond is not satisfied, the other node will draw it
                node.draw(surface)

        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius) #Drawing self
        if self.selected:
            pygame.draw.circle(surface, (0, 255, 0), (self.x, self.y), self.radius + 2, 2)


        if self.voltage is not None:
            # Display the voltage
            # Prepare the font
            font = pygame.font.Font(None, 24)  # You can adjust the size (24) as needed

            # Render the text (voltage in blue color)
            voltage_text = font.render(f"{self.voltage:.2f} V", True, (100, 100, 255))  # LightBlue color (RGB)

            # Calculate the position (slightly above and to the right of the node)
            text_x = self.x + self.radius + 5  # Adjust the offset as needed
            text_y = self.y - self.radius - 10

            # Draw the text on the screen
            screen.blit(voltage_text, (text_x, text_y))
    
 
    def handle_event(self, event, displacement):
        '''Handles the displacement and click event'''
        if self.event_handled == True: # To prevent multiple handling of the event from different parts of the graph
            return None
        self.event_handled = True
        #Translation handle
        self.x += displacement[0]
        self.y += displacement[1]

        #Event handle(we will only want to handle if build information is not present)
        if self.voltage is None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius).collidepoint(event.pos):
                # This if block handles clicking the node
                if self.selected == False:#Previous value
                    if Node.another_selected == False: # No other node is selected
                        #I need to add a temporary Wire
                        self.wires.append((Wire((self.x,self.y), pygame.mouse.get_pos(), True), None))
                        self.selected = True

                        #Changing global variables
                        Node.another_selected = True
                        Node.temporary_wire = self.wires[-1][0]
                        Node.selected_node = self

                    else:
                        #User wants to connect a wire between the nodes
                        #It is your responsibility to transfer the info to the node that it not need to be selected anymore
                        self.wires.append((Node.temporary_wire, Node.selected_node)) 

                        Node.temporary_wire.make_permanent(Node.selected_node, self)

                        #Updating the other nodes values
                        #Node.selected_node.wires.pop() #It is self's wire now
                        Node.selected_node.wires[-1] = (Node.temporary_wire, self)
                        Node.selected_node.selected = False

                        #Changing the static variables
                        Node.another_selected = False
                        Node.selected_node = None
                        Node.temporary_wire = None

                else:
                    #I need to remove the temporary wire
                    self.wires.pop()
                    self.selected = False

                    Node.another_selected = False
                    Node.selected_node = None
                    Node.temporary_wire = None

        assert self.voltage is None or not self.selected # selected => build is not done
        if self.selected:
            # Change the end point of the wire
            self.wires[-1][0].change_end_point(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Add a new node and make an interconnecting wire between those nodes
                self.selected = False # Not selected anymore
                node = Node(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
                self.wires[-1][0].make_permanent(self, node)
                self.wires[-1] = (self.wires[-1][0], node)
                node.wires.append((self.wires[-1][0], self))

                #Changing the global variables
                Node.another_selected = False
                Node.selected_node = None
                Node.temporary_wire = None


        for i in range(len(self.wires)):
            wire,node = self.wires[i]
            if node is None:
                # node is None => last wire is temporary
                wire.handle_event(event, displacement)
                continue
            if wire.is_transformation_request(event):
                if wire.resistor_form is None:
                    wire.resistor_form = Resistor(wire)
                self.wires[i] = wire.resistor_form, node # So that all the nodes share the same reference of the resistor
            if node.number > self.number:
                node.handle_event(event, displacement)
                wire.handle_event(event, displacement)
    
    def ingest_build_data(self, build_data):
        if not self.event_handled:
            self.voltage = build_data['voltages'][self.number]
            self.event_handled = True
            for wire, neighbour in self.wires:
                assert neighbour is not None
                neighbour.ingest_build_data(build_data)
                wire.ingest_build_data(build_data)

    def remove_build_data(self):
        if not self.event_handled:
            self.voltage = None
            self.event_handled = True
            for wire, neighbour in self.wires:
                assert neighbour is not None
                wire.remove_build_data()
                neighbour.remove_build_data()

class TextBox:
    other_selected = None # Represents any other text box that may be selected
    def __init__(self, value, suffix):
        self.text_rect = pygame.Rect(0, 0, 0, 0) # Initialize the rect
        # self.value = value # Default value
        self.str_val = str(value) # String representation of value
        self.suffix = suffix
        self.editing = False

    def end_editing(self):
        assert TextBox.other_selected == self
        TextBox.other_selected = None
        val = float(self.str_val)
        if val == int(val):
            val = int(val)
        self.str_val = str(val)
        self.editing = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.text_rect.collidepoint(event.pos):
            if self.editing:
                self.end_editing()
            else:
                if TextBox.other_selected is not None:
                    TextBox.other_selected.end_editing()
                TextBox.other_selected = self
                self.editing = True
        
        if self.editing and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:#An enter is a perfectly valid way of ending the editing cycle
                self.end_editing()
            elif event.key == pygame.K_BACKSPACE:
                if len(self.str_val) == 1:
                    self.str_val = '0'
                else:
                    self.str_val = self.str_val[:-1]
            elif pygame.K_PERIOD == event.key and '.' not in self.str_val:
                self.str_val += pygame.key.name(event.key)
            elif pygame.K_0 <= event.key <= pygame.K_9:
                if self.str_val == '0':
                    self.str_val = ''
                self.str_val += pygame.key.name(event.key)


    def draw(self, font_size, center, surface):
        font = pygame.font.Font(None, font_size)
        display_text = font.render(f"{self.str_val} {self.suffix}", True, (0, 0, 0))
        self.text_rect = display_text.get_rect(center=center)
        surface.blit(display_text, self.text_rect)
        if self.editing:
            pygame.draw.rect(surface, (255, 255, 0), self.text_rect, 2)


class Resistor(Wire):#A wrapper class
    def __init__(self, wire):
        self.wire: Wire = wire
        self.resistance = 5 # Default resistance
        self.resistance_box = TextBox(5, 'R')
        self.image = pygame.image.load('rsc/resistor.png').convert_alpha()
    
    def handle_event(self, event, displacement):
        self.wire.handle_event(None, displacement)#Does the translating buisness
        self.resistance_box.handle_event(event)
        self.resistance = float(self.resistance_box.str_val)

    def change_end_point(self, new_pos):
        # Probably will never be needed
        self.wire.change_end_point(new_pos)
    
    def get_resistance(self):
        return self.resistance
    
    def make_permanent(self):
        raise ValueError("Should never be called")

    def is_transformation_request(self, event):
        return False
    
    def ingest_build_data(self, build_data):
        self.wire.ingest_build_data(build_data)

    def remove_build_data(self):
        self.wire.remove_build_data()

    
    def draw(self, surface):
        #scaling
        dist = math.dist(self.wire.start_pos, self.wire.end_pos)
        scale_factor = dist / self.image.get_width()
        scaled_image = pygame.transform.scale(self.image, ((self.image.get_width() * scale_factor), (self.image.get_height() * 0.5)))
        
        #rotating
        angle = math.pi / 2
        if (self.wire.end_pos[0] - self.wire.start_pos[0]) != 0:
            angle = math.atan((self.wire.end_pos[1] - self.wire.start_pos[1])/ (self.wire.end_pos[0] - self.wire.start_pos[0]))
        angle = -math.degrees(angle)
        final_image = pygame.transform.rotate(scaled_image, angle)
        self.rect = final_image.get_rect()
        self.rect.center = (self.wire.start_pos[0] + (self.wire.end_pos[0] - self.wire.start_pos[0]) // 2, self.wire.start_pos[1] + (self.wire.end_pos[1] - self.wire.start_pos[1]) // 2)
        surface.blit(final_image, self.rect)

        # Drawing the resitance box
        angle = math.radians(angle)
        self.resistance_box.draw(
            60, 
            (self.rect.centerx - 50 * math.sin(angle), self.rect.centery - 50 * math.cos(angle)),
            surface
        )

        # Possible drawing of the current
        self.wire.draw_current(surface)

class Battery:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.offset = (0, 0)
        self.nodes = [Node(self.rect.left, self.rect.centery), Node(self.rect.right, self.rect.centery)]
        self.voltage = 5 # Default voltage
        self.voltage_box = TextBox(5, 'V')
        self.total_resistance = None

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.voltage_box.draw(80, (self.rect.centerx, self.rect.y - 20), surface)
        
        # Draw nodes
        for node in self.nodes:
            node.draw(surface)

        # Draw total resistance below the battery if it's not None
        if self.total_resistance is not None:
            font = pygame.font.Font(None, 40)
            resistance_text = font.render(f"Circuit Resistance: {self.total_resistance:.2f} R", True, (0, 0, 0))
            text_rect = resistance_text.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
            surface.blit(resistance_text, text_rect)


    def handle_event(self, event):
        self.nodes[0].handle_event(event, (self.rect.left - self.nodes[0].x, self.rect.centery - self.nodes[0].y))
        self.nodes[1].handle_event(event, (self.rect.right - self.nodes[1].x, self.rect.centery - self.nodes[1].y))
        for i in self.nodes:
            i.reset_event_handled()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.offset = (self.rect.x - event.pos[0], self.rect.y - event.pos[1])

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset[0]
                self.rect.y = event.pos[1] + self.offset[1]

        self.voltage_box.handle_event(event)
        self.voltage = float(self.voltage_box.str_val)
    
    def send_data(self):
        '''Performs a circuit traversal and stores the information of the graph in shared_file'''
        print("Building")        
        
        # Performs an initial dfs to check whether the circuit is closed
        visited = dict()
        for i in range(Node.total_nodes):
            visited[i] = False
        
        # Start from the left node
        stack: list[Node] = []
        stack.append(self.nodes[0])
        assert self.nodes[0].number == 0
        assert self.nodes[1].number == 1
        visited[0] = True # self.nodes[0].number is 0
        while stack:
            node = stack.pop()
            visited[node.number] = True
            for _, neighbour in node.wires:
                if not visited[neighbour.number]:
                    stack.append(neighbour)
                    visited[neighbour.number] = True
        
        if not visited[1]: # self.nodes[1].number is 1
            raise ValueError("The circuit is open")
        
        # Now we can just collect all the data and store it in the file
        # However, a small amount of refactoring needs to be done. Math.cpp assumes that
        # the node at 0V is n - 1. However, in my code, I have assumed it to be 1. So I will
        # just treat 1 as n - 1 and n - 1 as 1

        circuit_info = []
        # First line is the voltage
        circuit_info.append(str(self.voltage))

        # Second line is number of nodes
        circuit_info.append(f"\n{Node.total_nodes}")

        # The next lines consist of f"{node1} {node2} {resistance}"
        visited = dict()
        for i in range(Node.total_nodes):
            visited[i] = False
        
        stack: list[Node] = []
        stack.append(self.nodes[0])
        visited[0] = True

        resistance_info = []
        while stack:
            node = stack.pop()
            for wire, neighbour in node.wires:
                if node.number < neighbour.number:
                    # It is node's responsibility to add the resistance
                    resistance = wire.get_resistance()
                    num1 = node.number
                    num2 = neighbour.number
                    if num1 == 1:
                        num1 = Node.total_nodes - 1
                    elif num1 == Node.total_nodes - 1:
                        num1 = 1
                    
                    if num2 == 1:
                        num2 = Node.total_nodes - 1
                    elif num2 == Node.total_nodes - 1:
                        num2 = 1
                    resistance_info.append(f"\n{num1} {num2} {resistance}")

                if not visited[neighbour.number]:
                    visited[neighbour.number] = True
                    stack.append(neighbour)

        circuit_info.append(f"\n{len(resistance_info)}")
        circuit_info.extend(resistance_info)

        byte_form_data = (''.join(circuit_info)).encode('utf-8')

        # Now, calling the Interface subprocess
        # For now, I will always compile by default. In future steps, I would want to compile only if not compiled
        result = subprocess.run(
            [f"./build/Interface.out"],
            input = byte_form_data,
            capture_output = True,
            shell = True,
        )
        return result.stdout.decode()
        # except subprocess.CalledProcessError as e:
        #     print(f"Command failed with exit code {e.returncode}")
        #     print(f"Error message: {e.stderr}")
            
    
    def parse_data(self, received_data):
        data_lines = received_data.split('\n')
        build_info = dict()
        # Adding total resistance information
        build_info['total_resistance'] = float(data_lines[0])

        # Adding voltages data
        voltages = data_lines[1].split()
        for i in range(len(voltages)):
            voltages[i] = float(voltages[i])
        # Changing the voltages to match the formatting
        voltages[1], voltages[len(voltages) - 1] = voltages[len(voltages) - 1], voltages[1]
        build_info['voltages'] = voltages

        # Adding the current information
        current_info = dict()
        for i in range(2, len(data_lines)):
            node1, node2, current = data_lines[i].split()
            num1 = int(node1)
            num2 = int(node2)
            current = float(current)

            if num1 == 1:
                num1 = Node.total_nodes - 1
            elif num1 == Node.total_nodes - 1:
                num1 = 1
            
            if num2 == 1:
                num2 = Node.total_nodes - 1
            elif num2 == Node.total_nodes - 1:
                num2 = 1

            if num1 not in current_info:
                current_info[num1] = dict()
            if num2 not in current_info[num1]:
                current_info[num1][num2] = current
        build_info['current_info'] = current_info
        return build_info
    
    def perform_build(self):
        # Do not perform this if there is a temporary wire as it messes things up
        if Node.another_selected:
            raise ValueError("Cannot perform a build when another node is selected")
        
        # Sending the circuit data to the engine and receiving the results
        received_data = self.send_data()

        # Parsing the data
        build_info = self.parse_data(received_data)

        # Ingest build data
        self.ingest_build_data(build_info)

    def ingest_build_data(self, build_info: dict):
        '''Modifies the internal variables based on the build data and propogates it to other parts of the circuit'''
        self.total_resistance = build_info["total_resistance"]
        # Firstly, I will reset the nodes event_handled
        self.nodes[0].reset_event_handled()
        self.nodes[0].reset_event_handled()

        self.nodes[0].ingest_build_data(build_info)
        self.nodes[1].ingest_build_data(build_info)

        # Resetting it again(may not be required)
        self.nodes[0].reset_event_handled()
        self.nodes[1].reset_event_handled()

    def remove_build_data(self):
        '''
        When a build is done, the circuit has a bunch of metadata which will become invalid if any
        modification is made. To make a modification, we must remove the build data from every part
        of the circuit
        '''
        self.total_resistance = None
        # Firstly, I will reset the nodes event_handled
        self.nodes[0].reset_event_handled()
        self.nodes[1].reset_event_handled()

        self.nodes[0].remove_build_data()
        self.nodes[1].reset_event_handled()

        # Resetting it again(may not be required)
        self.nodes[0].reset_event_handled()
        self.nodes[1].reset_event_handled()


class Button:
    def __init__(self, x, y, image_path, dimensions):
        self.unscaled_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.unscaled_image, dimensions)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, event):
        # Returns whether the button has been clicked
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)
            
# Create Battery object
battery = Battery(100, 100, 'rsc/battery.png')  # x, y, image_path

# Creating the buttons
BUTTON_DIMENSIONS = (200, 200)
modify_button = Button(1400, 650, 'rsc/modify_button.png', BUTTON_DIMENSIONS)
reset_button = Button(1400, 800, 'rsc/reset_button.png', BUTTON_DIMENSIONS)
build_button = Button(1410, 950, 'rsc/build_button.png', BUTTON_DIMENSIONS)


# Initialize Pygame
pygame.init()

# Set up display
width, height = 1600, 1200
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Circuit Builder")

# Set up game loop variables
clock = pygame.time.Clock()
running = True

# Game loop
while running:
    # Circuit event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            battery.handle_event(event)
    
    # Reset button event handling
    if reset_button.is_clicked(event):
        Node.total_nodes = 0
        battery = Battery(100, 100, 'rsc/battery.png')

    # Build button event handling
    if build_button.is_clicked(event):
        battery.perform_build()

    has_built = battery.total_resistance is not None
    if has_built and modify_button.is_clicked(event):
        battery.remove_build_data()

    # Draw on the screen
    screen.fill((255, 255, 255))  # Fill screen with white color
    battery.draw(screen)
    reset_button.draw(screen)
    build_button.draw(screen)
    if has_built:
        modify_button.draw(screen)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()