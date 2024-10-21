# src/agent.py

from state_manager import StateManager
#from nlp_processor import NLPProcessor
from openai import OpenAI
import os
import readline
import sys
import textwrap
import json
from assistants.conversation import ConversationAssistant

class MyInputClass:
    def __init__(self):
        # Enable readline history and editing capabilities
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set editing-mode emacs")  # Enables Ctrl-A, Ctrl-E, etc.
        readline.parse_and_bind('"\\e[A": history-search-backward')  # Up arrow
        readline.parse_and_bind('"\\e[B": history-search-forward')   # Down arrow

    def read_input(self, prompt):

        try:
            # Read input from the prompt with enhanced capabilities
            user_input = input(prompt)
        except EOFError:
            # Handle EOF (Ctrl-D) gracefully
            print("\nInput interrupted.")
            return None

        return user_input


class Agent:
    def __init__(self, user_info, db_connection):
        self.user_info = user_info
        self.db = db_connection
        self.user_id = user_info['id']
        #self.db.delete_dimension_analysis(self.user_id)
        self.conversation_state = self.db.get_conversation_state(self.user_id)
        #self.nlp_processor = NLPProcessor()
        self.focus_dimension = None  # The dimension currently being focused on

        self.system_role = """
You are a Neuropsychologist Agent dedicated to helping users measure and improve their self-awareness
across multiple dimensions. Guide users on a personalized journey by providing insights and practical
tools related to consciousness, perception, attention, and self-awareness, using established
neuropsychological concepts and the latest neuroscience findings. Assist users with assessments, goal
setting, and developing personalized roadmaps with clear milestones. Navigate them through the main
states—Onboarding, DimensionAnalysis, Education, Practice, and Reflection—adapting conversations based
on the specific dimension being discussed. Communicate empathetically and supportively, using clear,
jargon-free language. Uphold confidentiality and privacy, respecting cultural sensitivities and ethical
boundaries. Your ultimate goal is to empower users to understand and improve their awareness dimensions,
 fostering self-efficacy and a growth mindset.
"""
        self.assistant_role = """
User Information
username: {self.user_info['username']},
birthdate: {self.user_info['birthdate']}
culture: {self.user_info['culture']}
"""

        self.state_manager = StateManager(agent=self)


    # Agent Main Loop
    # Checks the current state of the agent and either asks questsion or
    # waits for user input
    def main_loop(self):
        keep_going = True
        while keep_going:
            keep_going = self.state_manager.process_state()
            # if self.current_state == 'Conversation':
            #     user_input = input("> ")
            # else:
            #     user_input = None
            # response = self.state_manager.handle_input(user_input, intent=None)
            # print(response)
            # if self.current_state == 'Conversation':
            #     self.receive_input(user_input)
            # if self

    # Prints text to the screen using textwrap to limit to 100 characters per line
    def write(self, text, quiet=False):
        wrapped_text = textwrap.fill(
            text,
            width=100,
            initial_indent='    ',
            subsequent_indent='    ')
        if not quiet:
            print(wrapped_text)
        return wrapped_text

    def read_input(self, prompt):
        # Read input from the CLI prompt and use a known library to
        # allow for more complex input methods like ctrl-a, ctrl-e, upo down history, etc.
        input_class = MyInputClass()
        response = input_class.read_input(f"{prompt}\n\nUser:\n    > ")
        return response

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

    # Interact with ChatGPT via the Open AI API
    def get_response(self, prompt, model="gpt-4o-mini"):
        # Init OpenAI Client
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.getenv("OPENAI_API_KEY")
        )
        prompt_messages = []
        prompt_messages.append({"role": "system", "content": prompt['system_role']})

        # System Role Override
        # if 'system_role' in prompt.keys() and prompt['system_role'] is not None:
        #     prompt_messages.append({"role": "system", "content": prompt['system_role']})
        # else:
        #     prompt_messages.append({"role": "system", "content": self.system_role})
        # Assistant Role
        if 'assistant_role' in prompt.keys():
            prompt_messages.append({"role": "assistant", "content": prompt['assistant_role']})
        # User Prompt
        prompt_messages.append({"role": "user", "content": prompt['user_prompt']})
        completion = client.chat.completions.create(
            model=model,
            response_format={ "type": "json_object" },
            temperature=0.5,
            top_p=1.0,
            presence_penalty=0.0,
            messages=prompt_messages
        )

        #print(completion.choices[0].message.content)
        result = completion.choices[0].message.content

        return result

    # Handles the Agent conversation within a particular state
    def enter_conversation(self, prompt_context, assistant_role=None, agent_prompt=None, model="gpt-4o-mini", state=None, system_role=None):
        #print('--------------------------------------------------------------------')
        if agent_prompt is None:
            agent_prompt = self.conversation_state['next_agent_question']

        if assistant_role is None:
            assistant_role = self.db.get_conversation_events(self.user_id)

        state_obj = self.state_manager.state_class_obj[self.state_manager.state]
        # Display State and Commands
        self.state_manager.display_console_hud()
        wrapped_agent_prompt = self.write(agent_prompt, quiet=True)
        user_prompt = self.read_input(f"Agent:\n{wrapped_agent_prompt}")
        # Detect if the user has entered a command
        if user_prompt in state_obj.commands.keys():
            # Execute the command
            state_obj.commands[user_prompt]['handler']()
            return None
        prompt = {
            "user_prompt": f"{prompt_context}\n\nUser input:\n{user_prompt}",
            "assistant_role": f"{self.assistant_role}\n{state_obj.assistant_role}",
            "system_role": f"{self.system_role}\n{state_obj.system_role}",
        }
        results = self.get_response(
            prompt=prompt,
            model=model,
            system_role=system_role
        )
        conversation = {
            "user_input": user_prompt,
            "agent_response": results,
        }
        agent_response = json.loads(conversation['agent_response'])
        self.db.save_conversation_state(self.user_id, conversation['agent_response'])
        self.conversation_state = agent_response

        self.write(f"\nAgent:\n{agent_response['agent_response']}\n")

        conversation_assistant = ConversationAssistant(self)
        conversation_assistant.save_conversation(state, conversation)

        return conversation
