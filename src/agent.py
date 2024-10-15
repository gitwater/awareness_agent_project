# src/agent.py

from state_manager import StateManager
#from nlp_processor import NLPProcessor
from openai import OpenAI
import os
import readline

class MyInputClass:
    def read_input(self, prompt):
        # Enable readline history and editing capabilities
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set editing-mode emacs")  # Enables Ctrl-A, Ctrl-E, etc.
        readline.parse_and_bind('"\e[A": history-search-backward') # Up arrow
        readline.parse_and_bind('"\e[B": history-search-forward') # Down arrow

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
        self.state_manager = StateManager(agent=self)
        self.conversation_state = self.db.get_conversation_state(self.user_id)
        #self.nlp_processor = NLPProcessor()
        self.focus_dimension = None  # The dimension currently being focused on
        self.system_role = f"""You are a compassionate neuropsychologist helping {self.user_info['username']}, born {self.user_info['birthdate']}
from {self.user_info['culture']}, who has completed a self-awareness assessment. Based on their Awareness scores and profile information
you are tasked with analyzing and guiding the user to understand and improve their self awareness.

Use the following neurolpsychological domains to guide your analysis and recommendations:
Utilize the following neuropsychological domains to guide your analysis:

Attention and Concentration: Assist the user in understanding how their ability to focus and sustain attention affects their self-awareness and daily functioning.
Memory Functions: Help the user explore how their working memory, short-term memory, and long-term memory influence their cognitive processes and self-awareness.
Language Processing: Guide the user in recognizing how their receptive and expressive language abilities impact their communication skills and understanding of self and others.
Sensory-Motor Functions: Support the user in understanding how the integration of sensory input and motor output affects their physical awareness and interaction with the environment.
Perceptual Functions: Help the user comprehend how their visual-spatial abilities and object recognition influence their perception of the world and contribute to their self-awareness.
Executive Functions: Assist the user in understanding how their planning, decision-making, and inhibitory control affect their goal-directed behaviors and self-regulation.
Emotional Processing: Help the user explore how they perceive, interpret, and manage their emotions, and how this impacts their self-awareness and relationships.
Social Cognition: Guide the user in recognizing how they understand and interpret social cues and perspectives, influencing their interactions with others.
Metacognition: Support the user in understanding their ability to reflect on their own thoughts and cognitive processes, enhancing self-awareness.
Motivation and Reward Systems: Assist the user in understanding how their motivation and reward systems drive their behaviors and how leveraging these systems can enhance self-awareness and personal growth.

Your appoach to working with the user:
- Analyze and review the user's strengths and areas for growth based on their self-awareness profile.
- Working with the user on specific dimensions will involve:
    - Education around the dimensions from a neuropsychological and awe inspiring perspective of the human brain, mind, consciousness, and self-awareness.
    - Practices and techniques that naturally lead from the education and understanding of the dimensions.
    - Regular reviews and reflections on the user's progress and insights.
    - Work to create epiphanies by presenting information that is designed to resonate with the user based on their existing profile and detected awareness levels.
- Switch between the dimensions as needed to keep the user engaged and interested in their self-awareness journey.

DO NOT use markup language in any of your responses, this is used on an CLI.
"""

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
        prompt_messages.append({"role": "system", "content": self.system_role})
        prompt_messages.append({"role": "user", "content": prompt['user_prompt']})
        if 'assistant_role' in prompt.keys():
            prompt_messages.append({"role": "assistant", "content": prompt['assistant_role']})
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