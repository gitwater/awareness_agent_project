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

    # Handles the Agent conversation within a particular state
    def enter_conversation(self, prompt_context, assistant_role, agent_prompt=None, model="gpt-4o-mini"):
        print('--------------------------------------------------------------------')
        if agent_prompt is None:
            agent_prompt = self.agent.conversation_state['next_agent_question']

        wrapped_text = textwrap.fill(
            agent_prompt,
            width=100,
            initial_indent='    ',
            subsequent_indent='    ')
        user_input = self.agent.read_input(f"Agent:\n{wrapped_text}")
        prompt = {
            "system_role": self.agent.system_role,
            "user_prompt": f"{prompt_context}\n\nPlease answer this question from the user:\n{user_input}",
            "assistant_role": assistant_role,
        }
        results = self.agent.get_response(
            prompt=prompt,
            model=model,
        )
        conversation = {
            "user_input": user_input,
            "agent_response": results,
        }
        agent_response = json.loads(conversation['agent_response'])
        self.agent.db.save_conversation_state(self.agent.user_id, conversation['agent_response'])
        self.agent.conversation_state = agent_response
        # Print the resposne using textwrap to limit to 100 characters per line
        wrapped_text = textwrap.fill(
            agent_response['agent_response'],
            width=100,
            initial_indent='    ',
            subsequent_indent='    ')
        print(f"\nAgent:\n{wrapped_text}\n")

        #print('--------------------------------------------------------------------')
        self.save_conversation(conversation)

        return conversation

    def save_conversation(self, conversation):
        agent_response = json.loads(conversation['agent_response'])
        message = f"User: {conversation['user_input']}\nAgent: {agent_response['agent_response']}"
        message_history = self.agent.db.get_conversation_history(self.agent.user_id, self.state)
        save_conversation = True
        if message_history != None and len(message_history) > 0:
            # Check if the conversation already happened and decide if this one has any new information before saving
            # By asking the agent to compare the new conversation with the last one
            agent_prompt = f"""
            Last Conversation:
            User: {conversation['user_input']}
            Agent: {conversation['agent_response']}

            Start Message hisotory:
            {message_history}
            End Message hisotory:

            JSON response format:
            {{
                "save_conversation": true/false
            }}

            Comparing the last conversation with the message history, has a similar or exact conversation already occurred?
            If the new conversation provides new insights or information useful for agent context, then place 'true' in the save_conversation json field other wise set it to 'false'.
            """
            prompt = {
                'user_prompt': agent_prompt,
            }
            response = self.agent.get_response(prompt)
            save_conversation = json.loads(response)['save_conversation']

        if save_conversation == True:
            self.agent.db.save_conversation(self.agent.user_id, self.state, message)
