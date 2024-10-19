# An Agent Assistant class that manages system roles for various
# assistanted tasks.
from .base_assistant import Assistant

class ConversationAssistant( Assistant ):
    def __init__(self, agent):
        super().__init__(agent)

        self.INTENT_LIST = [
            "greeting",
            "farewell",
            "ask_question",
            "report_issue",
            "request_assistance",
            "provide_information",
            "express_gratitude",
            "express_apology",
            "confirm",
            "deny",
            "offer_solution",
            "express_dissatisfaction",
            "small_talk",
            "feedback",
            "status_update",
            "request_information",
            "provide_confirmation",
            "express_confusion",
            "request_clarification",
            "express_empathy",
            "other"
        ]

        self.ENTITY_TYPE_LIST = [
            "product",
            "service",
            "issue",
            "action",
            "credential",
            "personal_info",
            "authentication_issue",
            "delivery",
            "solution",
            "error_message",
            "feature",
            "date_time",
            "location",
            "contact_method",
            "payment",
            "account",
            "subscription",
            "technical_term",
            "order",
            "other"
        ]

        self.EMOTIONAL_TONE_LIST = [
            "neutral",
            "happy",
            "sad",
            "frustrated",
            "angry",
            "confused",
            "worried",
            "excited",
            "relieved",
            "disappointed",
            "apologetic",
            "grateful",
            "empathetic",
            "surprised",
            "polite",
            "impatient",
            "hopeful",
            "skeptical",
            "assertive",
            "other"
        ]


        self.system_role = """
You are an AI language assistant that processes dialogue exchanges between a user and an agent.
Your task is to extract essential metadata from each message to help maintain conversation
continuity and empathy in future interactions.

Instructions:
1. Process Each Message:
    * For each user/agent message exchange, generate a JSON object containing the following fields:
        * speaker
        * timestamp
        * intent
        * entities
        * emotionalTone
        * summary
2. Field Definitions and Extraction Guidelines:
    * speaker: Value: "user" or "agent".
        * Guideline: Identify who sent the message.
    * timestamp: Value: ISO 8601 format (e.g., "2023-10-19T16:00:00Z").
        * Guideline: Use the provided timestamp or generate the current UTC time if not given.
    * intent: Value: The primary intent of the message.
        * Guideline: Determine the main purpose of the message.
    * entities: Value: An array of objects, each with:
        * entity: The key term or phrase.
        * type: The category of the entity (e.g., "product", "issue", "action", etc).
        * Guideline: Extract significant nouns or noun phrases.
    * emotionalTone: Value: Detected emotion (e.g., "frustrated", "happy", "confused", etc).
        * Guideline: Identify any emotions expressed or implied.
    * summary: Value: A brief summary of the message content.
        * Guideline: Capture the essential information in one or two sentences.
3. Output Format:
    * Provide only the JSON object.
    * Ensure the JSON is properly formatted and valid.
    * Do not include any additional text or explanations.

JSON Output Format:
{
    "user": {
        "timestamp": "ISO 8601 format time when the message was received.",
        "intent": "Primary intent of the message (e.g., 'ask_question', 'report_issue').",
        "entities": [
            {
            "entity": "Key entity mentioned (e.g., 'delivery', 'account').",
            "type": "Type/category of the entity (e.g., 'service', 'personal_info')."
            }
        ],
        "emotionalTone": "Detected emotion (e.g., 'frustrated', 'happy', 'confused').",
        "summary": "A brief summary of the message content."
    },
    "agent": {
        <same fields as user>
    }
}
"""
        self.system_role += f"""
INTENT_VALUES: {self.INTENT_LIST}
ENTITY_TYPE_VALUES: {self.ENTITY_TYPE_LIST}
EMOTIONAL_TONE_VALUES: {self.EMOTIONAL_TONE_LIST}
"""

    def save_conversation(self, state, conversation):

        user_prompt = f"""
Message: {conversation['user_input']}
Speaker: user

Message: {conversation['agent_response']}
Speaker: agent
"""
        prompt = {
            'user_prompt': user_prompt,
            'system_role': self.system_role
        }
        response = self.agent.get_response(prompt, model="gpt-4o")

        self.agent.db.save_conversation_event(self.agent.user_id, state, response)