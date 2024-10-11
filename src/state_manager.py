# src/state_manager.py
from transitions import Machine
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

        self.state = None
        self.load_state()

        self.machine = Machine(model=self, states=StateManager.states, initial=self.state)
        self.machine.add_transition(trigger='to_DimensionAnalysis', source='Onboarding', dest='DimensionAnalysis')

    def load_state(self):
        saved_state_str = self.agent.db.get_agent_state(self.agent.user_id)
        # Convert json string to dict
        if saved_state_str:
            cur_state = json.loads(saved_state_str)
        else:
            cur_state = {
                'state': self.states[0]
            }

        self.state = cur_state['state']
        if self.state in cur_state.keys():
            self.sub_state = cur_state[self.state]['state']

    def save_state(self):
        saved_state_str = self.agent.db.get_agent_state(self.agent.user_id)
        # Convert json string to dict
        if saved_state_str:
            saved_state = json.loads(saved_state_str)
        else:
            saved_state = {
                'state': '',
            }

        saved_state['state'] = self.state
        saved_state[self.state] = { 'state': self.sub_state }
        new_state_str = json.dumps(saved_state)
        self.agent.db.save_agent_state(self.agent.user_id, new_state_str)

    def process_state(self):
        self.handlers[self.state]()
        self.save_state()

    def handle_Onboarding(self):
        self.state_class_obj['Onboarding'].process_state()

    def handle_DimensionAnalysis(self):
        self.state_class_obj['DimensionAnalysis'].process_state()

    @property
    def sub_state(self):
        return self.state_class_obj[self.state].state


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

class OnboardingState(BaseState):

    def __init__(self, state_manager, agent):
        states = ['Goals']
        super().__init__(state_manager, agent, states)

        self.handlers = {
            'Goals': self.handle_Goals,
        }

    def handle_Goals(self):
        print("Processing Onboarding.Goals")
        print("Thank you for providing your information. Let's proceed to analyze your profile.")
        self.state_manager.to_DimensionAnalysis()
        breakpoint()


class DimensionAnalysisState(BaseState):

    def __init__(self, state_manager, agent):
        states = ['Review', 'Roadmap']
        super().__init__(state_manager, agent, states)

        self.handlers = {
            'Review': self.handle_Review,
            'Roadmap': self.handle_Roadmap,
        }

        self.machine.add_transition(trigger='to_Roadmap', source='Review', dest='Roadmap')

    def handle_Review(self):
        print("Processing DimensionAnalysisState.Review")
        #self.to_substate_a2()
        self.to_Roadmap()
        breakpoint()

    def handle_Roadmap(self):
        print("Processing DimensionAnalysisState.Roadmap")
        #self.to_substate_a2()
        self.state_manager.to_Onboarding()
        breakpoint()

# class StateManager:
#     def __init__(self, agent):
#         self.agent = agent
#         self.state_handlers = {
#             'Onboarding': self.handle_onboarding,
#             'DimensionAnalysis': self.handle_dimension_analysis,
#             'InsightGathering': self.handle_insight_gathering,
#             'EducationalInfo': self.handle_educational_info,
#             'Planning': self.handle_planning,
#             'Conversation': self.handle_conversation,
#             'Assessment': self.handle_assessment,
#         }
#         self.onboarding_fields = ['age', 'gender', 'culture', 'language']
#         self.current_field_index = 0


#     def process_state(self):
#         handler = self.state_handlers.get(self.agent.current_state, self.handle_default)
#         handler(None, None)

#     def handle_input(self, user_input, intent):
#         handler = self.state_handlers.get(self.agent.current_state, self.handle_default)
#         return handler(user_input, intent)

#     def handle_onboarding(self, user_input, intent):
#         user_info = self.agent.user_info

#         return "Thank you for providing your information. Let's proceed to analyze your profile."

#     def handle_dimension_analysis(self, user_input, intent):
#         # Analyze profile and determine focus dimension
#         lowest_dimension = min(self.agent.user_profile, key=self.agent.user_profile.get)
#         self.agent.focus_dimension = lowest_dimension
#         self.agent.update_state('InsightGathering')
#         return f"Based on your profile, it seems we should focus on improving your '{lowest_dimension}'. Could you share more about your experiences related to this area?"

#     def handle_insight_gathering(self, user_input, intent):
#         # Process user's insights and proceed
#         self.agent.update_state('EducationalInfo')
#         return f"Thank you for sharing. I have some information that might help you understand '{self.agent.focus_dimension}' better."

#     def handle_educational_info(self, user_input, intent):
#         # Provide educational content
#         self.agent.update_state('Planning')
#         return f"Here is some educational content about '{self.agent.focus_dimension}':\n[Educational Content]\nDo you have any questions about this?"

#     def handle_planning(self, user_input, intent):
#         # Suggest improvement practices
#         self.agent.update_state('Conversation')
#         return f"Based on our discussion, I suggest the following practices to improve your '{self.agent.focus_dimension}':\n[Practice Suggestions]\nLet's stay in touch to monitor your progress."

#     def handle_conversation(self, user_input, intent):
#         # Ongoing support and conversation
#         if 'progress' in user_input.lower():
#             self.agent.update_state('Assessment')
#             return "Let's assess your progress. How do you feel about your improvement in this area?"
#         else:
#             return "I'm here to support you. How are you feeling today?"

#     def handle_assessment(self, user_input, intent):
#         # Reassess and update the profile
#         # For demonstration, increment the score
#         self.agent.user_profile[self.agent.focus_dimension] += 1
#         self.agent.db.save_profile(self.agent.user_id, self.agent.user_profile)
#         self.agent.update_state('Conversation')
#         return f"Great to hear! Your '{self.agent.focus_dimension}' score has improved. Let's continue working together."

#     def handle_default(self, user_input, intent):
#         return "I'm sorry, I didn't quite understand that. Could you please rephrase?"
