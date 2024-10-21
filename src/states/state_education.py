from .base_state import BaseState
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from math import pi
import textwrap
import json

class EducationState(BaseState):
    states = ['Introduction', 'Neuropsychology', 'Influences', 'Implications', 'Challenges', 'Culture', 'Advancements', 'Summary', 'Resources']

    def __init__(self, state, state_manager):
        super().__init__(state, state_manager)

        self.handlers = {
            'Introduction': self.handle_Introduction,
            # 'Neuropsychology': self.handle_Neuropsychology,
            # 'Influences': self.handle_Influences,
            # 'Implications': self.handle_Implications,
            # 'Challenges': self.handle_Challenges,
            # 'Culture': self.handle_Culture,
            # 'Advancements': self.handle_Advancements,
            # 'Summary': self.handle_Summary,
            # 'Resources': self.handle_Resources,
        }

    # Handle the Conversation
    def handle_Introduction(self):
        # Enter a conversation with the user asking them if they have any questions about the analysis
        prompt_context = f"""
You are now in a conversation with the user to provide Education on the top weakest dimensions of their self-awareness profile.
When you have detected the user would like to move on to the Practice state, indicate so in the json output.

Awareness Profile:
{self.agent.user_info['dimensions']}

Awareness Analysis:
{self.analysis_json}

JSON Response:
Rules:
next_detected_state: Detect if it seems like the user wants to switch to Analysis, Practice, or Reflection states, otherwise keep the current state.
Format:
{{
    "next_agent_action": "<Conversation, DisplayAnalysis, DisplaySpiderChart>",
    "next_detected_state": "<Analysis, Education, Practice, or Reflection>",
    "agent_response": "<place the agent response to the user here, but DO NOT place the the agent's next question here.>",
    "next_agent_question": "<agents next question here. Keep the current context unless the user wants to move on.>",
    "assistant_role": "<save any all conversation context information useful for the next prompt in this field>"
}}
"""
        conversation = self.agent.enter_conversation(
            prompt_context=prompt_context,
            agent_prompt=None,
            model='gpt-4o',
        )
        agent_response = json.loads(conversation['agent_response'])
        #if agent_response['next_detected_state'] == 'Education':
        #    self.to_Education()