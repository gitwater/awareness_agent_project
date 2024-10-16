from transitions import Machine
import json
import textwrap

class BaseState:
    def __init__(self, state_manager, agent, states):
        self.agent = agent
        self.state_manager = state_manager
        self.states = states
        self.state = self.states[0]  # Start with the first state by default
        self.handlers = {}
        self.machine = Machine(model=self, states=self.states, initial=self.state)

    def process_state(self):
        handler = self.handlers.get(self.state, self.handle_unknown_state)
        handler()

    def handle_unknown_state(self):
        print(f"Unknown state: {self.state}")
        # You can add logic to handle unknown states here


