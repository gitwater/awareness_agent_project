# src/nlp_processor.py

class NLPProcessor:
    def interpret_input(self, user_input):
        # Simple keyword-based intent recognition
        user_input = user_input.lower()
        if any(word in user_input for word in ['yes', 'sure', 'ok', 'affirmative', 'yeah', 'yep']):
            return 'affirmative'
        elif any(word in user_input for word in ['no', 'not', "don't", 'negative', 'nope']):
            return 'negative'
        elif '?' in user_input:
            return 'question'
        else:
            return 'statement'
