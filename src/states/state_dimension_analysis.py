from .base_state import BaseState
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from math import pi
import textwrap
import json

# Enable interactive mode
plt.ion()

def close_spider_chart():
    plt.close('all')  # Closes all open figures

def display_spider_chart(chart_file):
    if plt.get_fignums():
        plt.show()
    else:
        img = mpimg.imread(chart_file)
        imgplot = plt.imshow(img)
        plt.axis('off')  # Hide the axes

def generate_spider_chart(data, output_file):
    """
    Generates a Spider (Radar) Chart from the input JSON data.

    Args:
    data (dict): A dictionary containing 'labels' and 'scores' for the chart.
                 Example structure:
                 {
                     'spiderChartData': {
                         'labels': ['Label1', 'Label2', ...],
                         'scores': [Value1, Value2, ...]
                     }
                 }

    Returns:
    Displays a Spider Chart using Matplotlib.
    """

    # Extract labels and scores from the JSON data
    labels = data['spiderChartData']['labels']
    scores = data['spiderChartData']['scores']

    # Number of variables we're plotting
    num_vars = len(labels)

    # Compute angle of each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Complete the loop for the radar chart
    scores += scores[:1]
    angles += angles[:1]

    # Create the figure and axis for the spider chart with a larger figsize
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Plot the data
    ax.fill(angles, scores, color='red', alpha=0.25)
    ax.plot(angles, scores, color='red', linewidth=2)

    # Add the labels
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    # Ensure layout doesn't cut off the chart
    plt.tight_layout()

    plt.savefig(output_file)

    return plt

class DimensionAnalysisState(BaseState):

    def __init__(self, state_manager, agent):
        states = ['Analysis', 'Education', 'Practice', 'Reflection']
        super().__init__(state_manager, agent, states)

        self.handlers = {
            'Analysis': self.handle_Analysis,
            'Education': self.handle_Education,
        }

        self.sub_states = {
            'Analysis': ['analysis', 'conversation'],
            'Education': ['conversation']
        }

        self.sub_state = {
            'Analysis': self.sub_states['Analysis'][0],
            'Education': self.sub_states['Education'][0]
        }
        self.conversation_context = {
            'Analysis': "",
            'Education': "",
        }
        self.analysis_json = self.agent.db.get_dimension_analysis(self.agent.user_id)
        self.machine.add_transition(trigger='to_Education', source='Analysis', dest='Education')

    def set_sub_state(self, state, sub_state):
        self.sub_state[state] = sub_state

    # Generate a Spider Chart based on the user's Awareness Profile
    def gen_spider_chart(self):
        prompt = {
            # System Role
            'system_role': f"""You are a compassionate neuropsychologist helping {self.agent.user_info['username']}, born {self.agent.user_info['birthdate']}
             from {self.agent.user_info['culture']}, who has recently completed a self-awareness assessment. Based on their Awareness scores and profile information:
            {self.agent.user_info['dimensions']}
            , you are tasked with analyzing and guiding the user to understand and improve their self awareness.
            """,
            # User Prompt
            'user_prompt': f"""Based on the user's self-awareness profile analyze their strengths and weaknesses utilizing the following neuropsychological frameworks:

            - Create the data necessary to create a Spider Chart for each Dimension to show which dimensions are weak. Weaker dimensions will pull the line to the center of the Spider Chart.

JSON Response Format:
{{
    "spiderChartData": {{
        "labels": [],
        "scores": []
    }}
}}
"""
        }
        json_results = self.agent.get_response(prompt=prompt)
        results = json.loads(json_results)

        tmp_profile_spider_chart_file = '/tmp/profile-spider-chart.png'
        generate_spider_chart(results, tmp_profile_spider_chart_file)
        display_spider_chart(tmp_profile_spider_chart_file)


    def display_dimension_analysis(self, results):
        # Set the text width for wrapping and the indentation
        text_width = 100
        indent = ' ' * 4  # 4 spaces

        for category in ['Strengths', 'AreasForGrowth']:
            if category in results:
                print('--------------------------')
                print(category)
                print('--------------------------')
                dimensions = results[category]
                for dimension, details in dimensions.items():
                    print(dimension)
                    for key, value in details.items():
                        # Format the section title
                        section_title = key.replace('_', ' ').capitalize()
                        print(f"{indent}{section_title}:")
                        # Wrap the text with indentation
                        wrapped_text = textwrap.fill(value, width=text_width,
                                                    initial_indent=indent * 2,
                                                    subsequent_indent=indent * 2)
                        print(wrapped_text + '\n')
                    print('\n')

        # Display the summary section
        if 'summary' in results:
            print('--------------------------')
            print('Summary')
            print('-------\n')
            summary = results['summary']
            for key, value in summary.items():
                # Format the section title
                section_title = key.replace('_', ' ').capitalize()
                print(f"{indent}{section_title}:")
                # Wrap the text with indentation
                wrapped_text = textwrap.fill(value, width=text_width,
                                            initial_indent=indent * 2,
                                            subsequent_indent=indent * 2)
                print(wrapped_text + '\n')

        #print(f"Assistant Role:\n{results['assistant_role']}")

    def save_dimension_analysis(self, results):
        # Save the dimensional analysis results to the database for future reference
        # Save the results to the database for future reference
        self.agent.db.save_dimension_analysis(self.agent.user_id, results)

    def gen_analysis(self):
        # Use the agent to prompt ChatGPT to Analysis the profile and generate an
        # analysis and regommended next steps for the user
        prompt = {
            # User Prompt
            'user_prompt': f"""Based on the user's self-awareness profile analyze their strengths and weaknesses:

            - Choose the top two highest scoring dimensions to highlight as their strengths.
            - Choose the top two lowest scoring dimensions to highlight as areas for growth.
            - Be compassionate with non-judgmental, empathetic and supportive language.
            - Normalize the Experience and emphasize that everyone has areas to improve, and it's part of the human experience.
            - Be aware of how different dimensions interact
            - In the assistant_role save any information that will be useful when the user enters a conversation about the analysis.
Awareness Profile:
{self.agent.user_info['dimensions']}

JSON Response Format:
{{
    "Strengths": {{
        "<top strength dimension>": {{
            "score_understanding": "<description of how this strength impacts their self-awareness>",
            "why_this_matters": " "<description of how using this strength will benefit them>",
            "leveraging_this_strength": "<description of how they can leverage this strength to improve their self-awareness>",
            "an_interesting_fact": "<description that creates a sense of curiosity and awe to fostering epiphanies and insights>"
        }},
        "<second strength dimension>": {{ ... }},
    }},
    "AreasForGrowth": {{
        "<top growth dimension>": {{
            "score_understanding": "<description of how this weakness impacts their self-awareness>",
            "why_this_matters": " "<description of how improving this weakness will benefit them>",
            "leveraging_this_strength": "<description of how they can leverage this weakness to improve their self-awareness>",
            "an_interesting_fact": "<description that creates a sense of curiosity and awe to fostering epiphanies and insights>"
        }},
        "<second strength dimension>": {{ ... }},
    }},
    "summary": {{
        "growth_summary": "<summary of how the growth dimensions are releated and why they are important to address first and together>",
        "strength_summary": "<summary of how the strength dimensions are releated and how they can be leveraged together>",
        "next_steps": "<summary of how the agent will work with the user to improve their self-awareness moving forward>"
    }},
    "assistant_role": "<save info useful to the next prompt here>"
}}
"""
        }
        json_results = self.agent.get_response(prompt=prompt, model='gpt-4o')
        results = json.loads(json_results)
        return results


    # State: Analysis
    def handle_Analysis(self):
        #print("State: DimensionAnalysisState.Analysis")
        agent_prompt = "Do you have any questions about the analysis? "
        if self.analysis_json != None:
            analysis = json.loads(self.analysis_json)

        if self.sub_state['Analysis'] == 'analysis':
            print("Let's Analysis your Awareness dimension profile.")
            if self.analysis_json != None:
                print("Using existing analysis from the database.")
            else:
                print("Generating new analysis.")
                analysis = self.gen_analysis()
                self.save_dimension_analysis(analysis)
            #self.gen_spider_chart()
            self.display_dimension_analysis(analysis)
            self.set_sub_state('Analysis', 'conversation')
            self.conversation_context['Analysis'] = analysis['assistant_role']
        elif self.sub_state['Analysis'] == 'conversation':
            if self.conversation_context['Analysis']:
                agent_prompt = None

        # Enter a conversation with the user asking them if they have any questions about the analysis
        prompt_context = f"""
You are now in a conversation with the user to discuss the analysis of their self-awareness profile.
When you have detected the user would like to move on to the Eduaction state, indicate so in the json output.

Awareness Profile:
{self.agent.user_info['dimensions']}

Awareness Analysis:
{analysis}

JSON Response:
Rules:
next_detected_state: Should detect if the user wants to talk abou the Analysis, move on to Education, Practice or reflection, in that order.
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
            agent_prompt=agent_prompt, # To use the last agent prompt
            model='gpt-4o'
        )
        agent_response = json.loads(conversation['agent_response'])
        if agent_response['next_detected_state'] == 'Education':
            self.to_Education()


    # State: Education
    def handle_Education(self):
        #print("Processing DimensionAnalysisState.Education")
        self.set_sub_state('Education', 'conversation')

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