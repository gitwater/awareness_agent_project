
# Load BastState
from states.base_state import BaseState

from transitions import Machine

class OnboardingGoalsState(BaseState):
    #states = ['UserGoals', 'RecommendGoals']
    states = ['UserGoals']
    def __init__(self, state, state_manager):
        """Initialize with the parent state to access shared resources."""
        # Init super
        super().__init__(state, state_manager)

        self.state_system_role = """
In the 'Goals' substate, the Agent helps the user define their short-term and long-term goals
"""

        # Goals structure
        self.user_goals = self.agent.db.get_user_goals(self.agent.user_id) or {
            'short_term': [],
            'long_term': [],
            'completed': False
        }

        # Automate self.handlers
        for state in self.states:
            if hasattr(self, f"handle_{state}"):
                self.handlers[state] = getattr(self, f"handle_{state}")

        #self.machine.add_transition(trigger='to_RecommendGoals', source='UserGoals', dest='RecommendGoals')

    @property
    def assistant_role(self):
        return f"Onboarding Goals State: {self.state}"

    def handle_UserGoals(self):
        """Handles the 'Goals' substate"""
        self.agent.write("We are now in the 'Goals' substate.")

        agent_prompt = None
        if len(self.user_goals['short_term']) or len(self.user_goals['long_term']) == 0:
            agent_prompt = "What are your goals?"

        prompt_context = """"""
        # The Agent's Question
        # System Role: <Global Role><State Role><Substate Role>
        # Prompt Context:
        self.agent.enter_conversation(
            prompt_context=prompt_context,
            agent_prompt=agent_prompt, # To use the last agent prompt
            model='gpt-4o'
        )
        breakpoint()
        self.to_Roadmap()
        return True

