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

def display_snapshot_item(item_title, items):
    width = 80
    initial_indent = '    '
    subsequent_indent = '    '
    print(f"| {item_title}:\n")
    for item in items:
        # Print this print(f"{strength['dimension']}: {strength['description']}") with wrapping
        print(f"  {item['dimension']}")
        print(textwrap.fill(f"{item['description']}", width, initial_indent=initial_indent, subsequent_indent=subsequent_indent))
        print()

# Display the result of the Awareness Profile Snapshot
def display_snapshot(snapshot):
    # Convert finding result json sgring into python dict

    # Display the snapshot to the user in a readable format by printing the Synopis, Strengths, and Weaknesses
    # of the user's awareness profile.
    print("-------------------------------------------------------------------------------")
    print("Awareness Profile Analysis")
    print("-------------------------------------------------------------------------------")
    # Print the Synopsis
    #print("Synopsis:")
    #print(snapshot['synopsis']['Guidance'])
    #print("-------------------------------------------------------------------------------")
    # Print the Strengths
    # loop through synopsys items and display items
    for (item_title, item) in snapshot['synopsis'].items():
        display_snapshot_item(item_title, item)
        print("-------------------------------------------------------------------------------")

    # #display_snapshot_item("Strengths", snapshot['synopsis']['Strengths'])
    # print("- Strengths -\n")
    # for strength in snapshot['synopsis']['Strengths']:
    #     # Print this print(f"{strength['dimension']}: {strength['description']}") with wrapping
    #     print(f"{strength['dimension']}")
    #     print(textwrap.fill(f"{strength['description']}", width=60, initial_indent='    ', subsequent_indent='    '))
    #     print()
    # print("-------------------------------------------------------------------------------")
    # # Print the Weaknesses
    # print("Weaknesses:")
    # for weakness in snapshot['synopsis']['Weaknesses']:
    #     print(f"{weakness['dimension']}: {weakness['description']}")
    # print("-------------------------------------------------------------------------------")
    # print("Relationships:")
    # for relationship in snapshot['synopsis']['Relationships']:
    #     print(f"{relationship['Connection']} from {relationship['From']} to {relationship['To']}")
    # print("-------------------------------------------------------------------------------")

    # Generate a

    #generate_spider_chart(snapshot, output_file=os.path.join(output_path, 'profile-spider-chart.png'))

    return snapshot

class DimensionAnalysisState(BaseState):

    def __init__(self, state_manager, agent):
        states = ['Review', 'Education', 'Practice']
        super().__init__(state_manager, agent, states)

        self.handlers = {
            'Review': self.handle_Review,
            'Education': self.handle_Education,
        }

        self.machine.add_transition(trigger='to_Education', source='Review', dest='Education')

    def handle_Review(self):
        print("Processing DimensionAnalysisState.Review")
        print("Let's review your Awareness dimensional profile.")
        # Use the agent to prompt ChatGPT to review the profile and generate an
        # analysis and regommended next steps for the user
        prompt = {

            'system_role': f"""You are a compassionate neuropsychologist helping {self.agent.user_info['username']}, born {self.agent.user_info['birthdate']}
             from {self.agent.user_info['culture']}, who has recently completed a self-awareness assessment. Based on the following scores in json format:
            {self.agent.user_info['dimensions']}
            , you are tasked with generating a snapshot of their awareness profile and providing guidance on how to improve their self-awareness.
            """,
            'user_prompt': f"""Provide a personalized, encouraging summary that:

            - Highlights their strengths.
            - Identifies key areas for growth.
            - Explains why focusing on these areas will benefit them.
            - Uses language suitable for someone with a their current understanding of self-awareness concepts based on their assessment results.
            - Create the data necessary to create a Spider Chart for each Dimension to show which dimensions are weak. Weaker dimensions will pull the line to the center of the Spider Chart.

JSON Response Format:
{{
    "spiderChartData": {{
        "labels": [],
        "scores": []
    }},
    "synopsis": {{
        "Strengths": [{{"dimension": "", "description": ""}}],
        "AreasForGrowth": [{{"dimension": "", "description": ""}}],
    }}
}}

Awareness Profile:
{self.agent.user_info.get('dimensions')}
"""
        }
        json_results = self.agent.get_response(prompt)
        results = json.loads(json_results)

        tmp_profile_spider_chart_file = '/tmp/profile-spider-chart.png'
        generate_spider_chart(results, tmp_profile_spider_chart_file)
        display_spider_chart(tmp_profile_spider_chart_file)
        display_snapshot(results)
        breakpoint()
        self.to_Education()
        breakpoint()

    def handle_Education(self):
        print("Processing DimensionAnalysisState.Education")
        #self.to_substate_a2()
        self.state_manager.to_Onboarding()
        breakpoint()