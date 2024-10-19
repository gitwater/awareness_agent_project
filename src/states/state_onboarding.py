from .base_state import BaseState

class OnboardingState(BaseState):

    def __init__(self, state_manager, agent):
        sub_states = ['Goals']
        super().__init__(state_manager, agent, sub_states)

        self.handlers = {
            'Goals': self.handle_Goals,
        }

    def handle_Goals(self):
        print("Processing Onboarding.Goals")
        print("Thank you for providing your information. Let's proceed to analyze your profile.")
        self.state_manager.to_DimensionAnalysis()
        #breakpoint()