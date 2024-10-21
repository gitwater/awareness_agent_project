from transitions import Machine
import json
import textwrap

class BaseState:
    def __init__(self, state, state_manager):
        self.name = state
        self.agent = state_manager.agent
        self.state_manager = state_manager
        # if self.state doesnot exist set self.state to the first state in the list
        if getattr(self, 'state', None) is None:
            self.state = self.states[0]

        # State Class Object and Handlers
        self.state_class_obj = {}
        self.handlers = {}
        # State Machine Init
        self.machine = Machine(model=self, states=self.states, initial=self.state)

        self.commands = {}
        self.add_command('quit', self.quit, 'Quit the Agent')

    def init_state(self):
        pass

    @property
    def system_role(self):
        return f"{self.state_system_role}"

    @property
    def state_class(self):
        return self.state_class_obj[self.state]

    def process_state(self):
        handler = self.handlers.get(self.state, self.handle_unknown_state)
        handler()

    def handle_unknown_state(self):
        print(f"Unknown state: {self.name}.{self.state}")
        # You can add logic to handle unknown states here
        breakpoint()

    def add_command(self, command, handler, description):
        self.commands[command] = {
            'handler': handler,
            'description': description
        }

    def quit(self):
        print("Quitting...")
        exit()


