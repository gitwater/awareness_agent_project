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
        states = ['Analysis', 'Conversation']
        super().__init__(state_manager, agent, states)

        self.handlers = {
            'Analysis': self.handle_Analysis,
            'Conversation': self.handle_Conversation,
        }

        self.machine.add_transition(trigger='to_Conversation', source='Analysis', dest='Conversation')

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
        json_results = self.agent.get_response(prompt)
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
                print('-------')
                print(category)
                print('-------\n')
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
            print('-------')
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

        print(f"Prompt Context:\n{results['prompt_context']}")

    def save_dimension_analysis(self, results):
        # Save the dimensional analysis results to the database for future reference
        # Save the results to the database for future reference
        self.agent.db.save_dimension_analysis(self.agent.user_info['id'], results)
        pass

    def gen_analysis(self):
        # Use the agent to prompt ChatGPT to Analysis the profile and generate an
        # analysis and regommended next steps for the user
        prompt = {
            # System Role
            'system_role': f"""You are a compassionate neuropsychologist helping {self.agent.user_info['username']}, born {self.agent.user_info['birthdate']}
             from {self.agent.user_info['culture']}, who has recently completed a self-awareness assessment. Based on their Awareness scores and profile information:
            {self.agent.user_info['dimensions']}
            , you are tasked with analyzing and guiding the user to understand and improve their self awareness.

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
            """,
            # User Prompt
            'user_prompt': f"""Based on the user's self-awareness profile analyze their strengths and weaknesses:

            - Choose the top two highest scoring dimensions to highlight as their strengths.
            - Choose the top two lowest scoring dimensions to highlight as areas for growth.
            - Be compassionate with non-judgmental, empathetic and supportive language.
            - Normalize the Experience and emphasize that everyone has areas to improve, and it's part of the human experience.
            - Be aware of how different dimensions interact
            - In the prompt_context save any information that will be useful to send in the next prompt for DimensionAnalysis.

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
    }}
    "prompt_context": ""
}}
"""
        }
        json_results = self.agent.get_response(prompt, 'gpt-4o')
        results = json.loads(json_results)
        return results

    def handle_Analysis(self):
        print("Processing DimensionAnalysisState.Analysis")
        print("Let's Analysis your Awareness dimension profile.")

        analysis = self.agent.db.get_dimension_analysis(self.agent.user_info['id'])
        if analysis:
            print("Using existing analysis from the database.")
            results = json.loads(analysis)
        else:
            print("Generating new analysis.")
            results = self.gen_analysis()
        #self.gen_spider_chart()
        self.display_dimension_analysis(results)
        self.save_dimension_analysis(results)
        self.to_Conversation()

    def handle_Conversation(self):
        print("Processing DimensionAnalysisState.Conversation")
        #self.to_substate_a2()
        self.state_manager.to_Onboarding()
        breakpoint()