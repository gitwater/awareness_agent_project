from transitions import Machine
import json
import textwrap

class BaseState:
    def __init__(self, state_manager, agent, sub_states):
        self.agent = agent
        self.state_manager = state_manager
        self.sub_states = sub_states
        self.sub_state = self.sub_states[0]  # Start with the first state by default
        self.handlers = {}
        self.machine = Machine(model=self, states=self.sub_states, initial=self.sub_state)
        # Command format: {command: {handler: handler, description: description}}
        self.commands = {}
        self.add_command('quit', self.quit, 'Quit the Agent')

    def process_state(self):
        handler = self.handlers.get(self.sub_state, self.handle_unknown_state)
        handler()

    def handle_unknown_state(self):
        print(f"Unknown state: {self.sub_state}")
        # You can add logic to handle unknown states here

    def add_command(self, command, handler, description):
        self.commands[command] = {
            'handler': handler,
            'description': description
        }

    def quit(self):
        print("Quitting...")
        exit()


