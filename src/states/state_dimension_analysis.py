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

        sub_states = ['Analysis', 'SpiderChart']
        super().__init__(state_manager, agent, sub_states)

        self.add_command('show spider chart', self.display_spider_chart, description='Display the Spider Chart')
        self.add_command('show analysis', self.display_dimension_analysis, description='Display the Dimensional Analysis')

        self.handlers = {
            'Analysis': self.handle_Analysis,
            'SpiderChart': self.handle_SpiderChart,
        }

        # Generate the Dimensional Analysis if it does not exist
        self.analysis = None
        self.analysis_json = self.agent.db.get_dimension_analysis(self.agent.user_id)
        if self.analysis_json == None:
            self.gen_analysis()
        else:
            self.analysis = json.loads(self.analysis_json)

        # Spider Chart Data
        self.spider_chart_data_json = None

        self.machine.add_transition(trigger='to_SpiderChart', source='Analysis', dest='SpiderChart')
        self.machine.add_transition(trigger='to_Analysis', source='SpiderChart', dest='Analysis')

    # Generate a Spider Chart based on the user's Awareness Profile
    def display_spider_chart(self):
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
        self.spider_chart_data_json = json_results
        tmp_profile_spider_chart_file = '/tmp/profile-spider-chart.png'
        generate_spider_chart(results, tmp_profile_spider_chart_file)
        display_spider_chart(tmp_profile_spider_chart_file)
        self.to_SpiderChart()


    def display_dimension_analysis(self):
        # Set the text width for wrapping and the indentation
        text_width = 100
        indent = ' ' * 4  # 4 spaces
        for category in ['Strengths', 'AreasForGrowth']:
            if category in self.analysis:
                print('--------------------------')
                print(category)
                print('--------------------------')
                dimensions = self.analysis[category]
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
        if 'summary' in self.analysis:
            print('--------------------------')
            print('Summary')
            print('-------\n')
            summary = self.analysis['summary']
            for key, value in summary.items():
                # Format the section title
                section_title = key.replace('_', ' ').capitalize()
                print(f"{indent}{section_title}:")
                # Wrap the text with indentation
                wrapped_text = textwrap.fill(value, width=text_width,
                                            initial_indent=indent * 2,
                                            subsequent_indent=indent * 2)
                print(wrapped_text + '\n')
        self.to_Analysis()

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
        self.analysis_json = json_results
        results = json.loads(json_results)
        self.analysis = results
        self.agent.db.save_dimension_analysis(self.agent.user_id, json_results)
        return

    def process_state(self):
        # Call super to process the state
        super().process_state()

    def enter_conversation(self, prompt_context, agent_prompt):
        self.agent.enter_conversation(
            prompt_context=prompt_context,
            agent_prompt=agent_prompt, # To use the last agent prompt
            model='gpt-4o'
        )
        return True

    # State: Analysis
    def handle_Analysis(self):
        # Customize the role and prompt for the Analysis sub state
        agent_prompt = "Do you have any questions about the analysis? "
        agent_prompt = None
        # Enter a conversation with the user asking them if they have any questions about the analysis
        prompt_context = f"""
You are now in a conversation with the user to discuss the analysis of their self-awareness profile.
When you have detected the user would like to move on to the Eduaction state, indicate so in the json output.

Awareness Profile:
{self.agent.user_info['dimensions']}

Dimensional Analysis:
{self.analysis_json}

JSON Response:
Rules:
next_detected_state: Should detect if the user wants to talk about the Analysis, move on to Education, Practice or reflection, in that order.
Format:
{{
    "next_agent_action": "<Conversation, DisplayAnalysis, DisplaySpiderChart>",
    "next_detected_state": "<Analysis, Education, Practice, or Reflection>",
    "agent_response": "<place the agent response to the user here, but DO NOT place the the agent's next question here.>",
    "next_agent_question": "<agents next question here. Keep the current context unless the user wants to move on.>",
    "assistant_role": "<save any all conversation context information useful for the next prompt in this field>"
}}
"""
        return self.enter_conversation(prompt_context, agent_prompt)

    def handle_SpiderChart(self):
        # Customize the role and prompt for the Analysis sub state
        agent_prompt = None
        # Enter a conversation with the user asking them if they have any questions about the analysis
        prompt_context = f"""
You have generated and displayed a Spider Chart of the users dimension profile.

Have a conversation with the user to discuss the Spider Chart and answer any questions they may have.

Awareness Profile:
{self.agent.user_info['dimensions']}

Spider Chart Data:
{self.spider_chart_data_json}

JSON Response Format:
Rules:
next_detected_state: Should detect if the user wants to talk about the Analysis, move on to Education, Practice or reflection, in that order.
Format:
{{
    "next_agent_action": "<DiscussSpiderChart, DiscussAnalysis, SwitchTopics>",
    "next_detected_state": "<Analysis, Education, Practice, or Reflection>",
    "agent_response": "<place the agent response to the user here, but DO NOT place the the agent's next question here.>",
    "next_agent_question": "<agents next question here. Keep the current context unless the user wants to move on.>",
    "assistant_role": "<save any all conversation context information useful for the next prompt in this field>"
}}
"""
        return self.enter_conversation(prompt_context, agent_prompt)