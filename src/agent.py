# src/agent.py

from state_manager import StateManager
from nlp_processor import NLPProcessor

class Agent:
    def __init__(self, user_info, db_connection, user_id=None):
        self.user_info = user_info
        self.db = db_connection
        self.user_id = user_id
        self.state_manager = StateManager(agent=self)
        self.nlp_processor = NLPProcessor()
        self.focus_dimension = None  # The dimension currently being focused on

    # Agent Main Loop
    # Checks the current state of the agent and either asks questsion or
    # waits for user input
    def main_loop(self):
        while True:
            self.state_manager.process_state()
            # if self.current_state == 'Conversation':
            #     user_input = input("> ")
            # else:
            #     user_input = None
            # response = self.state_manager.handle_input(user_input, intent=None)
            # print(response)
            # if self.current_state == 'Conversation':
            #     self.receive_input(user_input)
            # if self

    def receive_input(self, user_input):
        # Save user input to conversation history
        #self.db.save_conversation(self.user_id, user_input, sender='user')
        # Process user input
        #intent = self.nlp_processor.interpret_input(user_input)
        intent = None
        # Get response from state manager
        response = self.state_manager.handle_input(user_input, intent)
        # Save agent response to conversation history
        #self.db.save_conversation(self.user_id, response, sender='agent')
        return response

    def update_state(self, new_state):
        self.current_state = new_state
        self.db.update_agent_state(self.user_id, self.current_state)
