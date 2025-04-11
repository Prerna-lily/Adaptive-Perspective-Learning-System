# Adaptive Perspective Learning System (APLS) Agent
# Author: [Your Name or Org]

import difflib
from datetime import datetime
from typing import List, Tuple, Dict
import openai
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# ----------------------
# Managed AI Service Interface (OpenAI)
# ----------------------
class OpenAIService:
    def __init__(self, model: str = "gpt-4"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model

    def generate_content(self, prompt: str, profile):
        system_prompt = f"Generate content in a '{profile.style_tone or 'neutral'}' tone using client vocabulary: {', '.join(profile.preferred_vocab)}."
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']

    def detect_tone(self, text: str) -> str:
        tone_prompt = f"What is the tone of the following sentence? Respond with a single word tone: '{text}'"
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "user", "content": tone_prompt}
            ]
        )
        return response.choices[0].message['content'].strip().lower()

# ----------------------
# Data Structure for Perspective Profile
# ----------------------
class PerspectiveProfile:
    def __init__(self, client_id):
        self.client_id = client_id
        self.style_tone = ""
        self.preferred_vocab = []
        self.perspective_patterns = []
        self.last_updated = datetime.now()

    def update_pattern(self, pattern_text, pattern_type):
        for pattern in self.perspective_patterns:
            if pattern['pattern'] == pattern_text:
                pattern['frequency'] += 1
                break
        else:
            self.perspective_patterns.append({
                "pattern": pattern_text,
                "frequency": 1,
                "type": pattern_type
            })
        self.last_updated = datetime.now()

    def update_vocab(self, new_word: str):
        if new_word not in self.preferred_vocab:
            self.preferred_vocab.append(new_word)

    def update_tone(self, tone: str):
        if tone and tone != self.style_tone:
            self.style_tone = tone

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "style_tone": self.style_tone,
            "preferred_vocab": self.preferred_vocab,
            "perspective_patterns": self.perspective_patterns,
            "last_updated": self.last_updated.isoformat()
        }

    def save_to_file(self):
        filename = f"profile_{self.client_id}.json"
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

# ----------------------
# Pattern Identification Logic
# ----------------------
def identify_edit_patterns(original: str, revised: str) -> Dict:
    diff = list(difflib.ndiff(original.split(), revised.split()))
    changes = {'insertions': [], 'deletions': [], 'replacements': []}
    prev_word = ""
    for d in diff:
        if d.startswith('- '):
            prev_word = d[2:]
        elif d.startswith('+ '):
            if prev_word:
                changes['replacements'].append((prev_word, d[2:]))
                prev_word = ""
            else:
                changes['insertions'].append(d[2:])
        elif d.startswith('? '):
            continue
    return changes

# ----------------------
# Edit Classification
# ----------------------
def classify_edit(pattern: Tuple[str, str], frequency_threshold: int = 3) -> str:
    stylistic_indicators = ["and", "is", "the", "a"]
    substantive_indicators = ["optimize", "strategic", "platform", "innovative"]

    if pattern[0].lower() in stylistic_indicators or pattern[1].lower() in stylistic_indicators:
        return "stylistic"
    elif pattern[0].lower() in substantive_indicators or pattern[1].lower() in substantive_indicators:
        return "substantive"
    return "stylistic" if frequency_threshold < 3 else "substantive"

# ----------------------
# Main Learning Agent
# ----------------------
class AdaptivePerspectiveAgent:
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.client_profiles = {}

    def register_client(self, client_id: str):
        self.client_profiles[client_id] = PerspectiveProfile(client_id)

    def generate_with_profile(self, client_id: str, prompt: str) -> str:
        profile = self.client_profiles.get(client_id)
        return self.ai_service.generate_content(prompt, profile)

    def learn_from_feedback(self, client_id: str, original: str, approved: str):
        profile = self.client_profiles.get(client_id)
        if not profile:
            raise Exception("Client not registered")

        changes = identify_edit_patterns(original, approved)
        print("Detected Changes:", changes)

        for old, new in changes['replacements']:
            pattern_type = classify_edit((old, new))
            profile.update_pattern(f"replaces '{old}' with '{new}'", pattern_type)
            if pattern_type == "substantive":
                profile.update_vocab(new)

        tone = self.ai_service.detect_tone(approved)
        profile.update_tone(tone)
        profile.last_updated = datetime.now()
        profile.save_to_file()

# ----------------------
# Example Usage
# ----------------------
if __name__ == '__main__':
    ai_service = OpenAIService()
    agent = AdaptivePerspectiveAgent(ai_service=ai_service)

    client_id = "acme-001"
    agent.register_client(client_id)

    prompt = "Our product is great."
    generated = agent.generate_with_profile(client_id, prompt)
    print("Generated Draft:\n", generated)

    approved_version = "Our platform is innovative."
    agent.learn_from_feedback(client_id, prompt, approved_version)

    print("\nUpdated Client Profile:")
    print(json.dumps(agent.client_profiles[client_id].to_dict(), indent=2))
