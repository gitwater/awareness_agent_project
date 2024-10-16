# src/state_manager.py
from transitions import Machine
from states.state_onboarding import OnboardingState
from states.state_dimension_analysis import DimensionAnalysisState
import json

class StateManager:
    states = ['Onboarding', 'DimensionAnalysis']

    def __init__(self, agent):
        self.handlers = {
            'Onboarding': self.handle_Onboarding,
            'DimensionAnalysis': self.handle_DimensionAnalysis,
        }
        self.state_class_obj = {
            'Onboarding': OnboardingState(self, agent),
            'DimensionAnalysis': DimensionAnalysisState(self, agent),
        }

        self.agent = agent

        self.global_state = {
            'state': self.states[0],
            'states': {}
        }
        #self.sub_state = None
        self.load_state()

        self.machine = Machine(model=self, states=StateManager.states, initial=self.state)
        self.machine.add_transition(trigger='to_DimensionAnalysis', source='Onboarding', dest='DimensionAnalysis')


    def load_state(self):
        saved_state_str = self.agent.db.get_agent_state(self.agent.user_id)
        # Convert json string to dict
        if saved_state_str:
            cur_state = json.loads(saved_state_str)
            self.global_state = cur_state
            for state in cur_state['states'].keys():
                self.state_class_obj[state].state = cur_state['states'][state]['state']

        self.state = self.global_state['state']

    def save_state(self):

        saved_state = {
            'state': self.state,
            'states': {
            },
        }

        for state in self.states:
            saved_state['states'][state] = { 'state': self.state_class_obj[state].state }

        new_state_str = json.dumps(saved_state)
        self.agent.db.save_agent_state(self.agent.user_id, new_state_str)

    def process_state(self):
        self.handlers[self.state]()
        self.save_state()

    def handle_Onboarding(self):
        self.state_class_obj['Onboarding'].process_state()

    def handle_DimensionAnalysis(self):
        self.state_class_obj['DimensionAnalysis'].process_state()

    # Enters this state when the agent is ready to have a conversation with the user.
    # This happens for example after onboarding and Dimension Analysis is complete.
    # All conversation states will have a consistent workflow with context passed
    # in from the existing state
    def handle_StateConversation(self):
        pass

    @property
    def sub_state(self):
        return self.state_class_obj[self.state].state