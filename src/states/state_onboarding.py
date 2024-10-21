from .base_state import BaseState
from .onboarding.onboarding_goals import OnboardingGoalsState

class OnboardingState(BaseState):
    #states = ['Introduction', 'Questionnaire', 'Goals', 'Roadmap']
    states = ['OnboardingGoals']

    def __init__(self, state, state_manager):

        super().__init__(state, state_manager)

        self.state_system_role = """
You are in the Onboarding state. Your role is to welcome and guide users through the initial setup.
Help them complete the awareness questionnaire, explain the program's purpose and benefits, and
assist in articulating their short-term and long-term goals. Provide clear instructions and answer
any questions they may have. Use an empathetic and supportive tone to make the user feel comfortable
and engaged. Ensure communication is concise and jargon-free, establishing a strong foundation for
their self-awareness journey.
"""

        # self.handlers = {
        #     'Introduction': self.handle_Introduction,
        #     'Questionnaire': self.handle_Questionnaire,
        #     'Goals': self.state_class_obj['Goals'].handle_UserGoals,
        #     'Roadmap': self.handle_Roadmap
        # }

        for state in self.states:
            state_class = globals()[f"{state}State"]
            self.state_class_obj[state] = state_class(state, state_manager)
            if hasattr(self, f"handle_{state}"):
                self.handlers[state] = getattr(self, f"handle_{state}")

        # self.machine.add_transition(trigger='to_Questionnaire', source='Introduction', dest='Questionnaire')
        # self.machine.add_transition(trigger='to_Goals', source='Questionnaire', dest='Goals')
        # self.machine.add_transition(trigger='to_Roadmap', source='Goals', dest='Roadmap')

    @property
    def system_role(self):
        return f"{self.state_system_role}\n{self.state_class.system_role}"

    @property
    def assistant_role(self):
        state_assitant_role = f"Onboarding State: {self.state}"
        return f"{state_assitant_role}\n{self.state_class.assistant_role}"

    # Agent Introductes itself to the user
    def handle_Introduction(self):
        self.agent.write("Welcome! I’m excited to guide you through this journey of self-discovery. We'll begin by getting to know each other, and then I'll ask you a few questions to help understand your needs better. Once we've gathered your responses, I'll provide a personalized report with insights just for you. From there, I'll share a roadmap tailored to support your growth and well-being, helping you take the next steps with confidence.\n")
        self.to_Questionnaire()

    def handle_Questionnaire(self):
        self.agent.write("Questionnaire: Completed")
        self.to_Goals()

    def handle_OnboardingGoals(self):
        self.state_class_obj['OnboardingGoals'].process_state()

    def handle_Roadmap(self):
        self.agent.write("Roadmap")
        self.state_manager.to_Education()
