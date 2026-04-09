import ollama
import json
import threading
from app.routes.functions import get_function_schemas
# Lazy import memory/rag to avoid circular deps during init if any

class LLMAgent:
    def __init__(self, model_name="qwen2.5:3b"):
        self.model_name = model_name
        self.system_prompt = self._build_system_prompt()
        self.memory = None
        self.ayurveda = None

    def _init_resources(self):
        if not self.memory:
            from app.ai.memory import MemoryModel
            from app.ai.rag_ayurveda import AyurvedaKnowledgeBase
            self.memory = MemoryModel(index_file="app_memory.index", store_file="app_store.pkl")
            self.ayurveda = AyurvedaKnowledgeBase()

    def _build_system_prompt(self):
        tools = get_function_schemas()
        return f"""
        You are ELDA, a compassionate AI Caregiver for an Alzheimer's patient.
        Your goal is to provide emotional support and navigate the patient through their day.
        
        CRITICAL INSTRUCTION:
        You can control the patient's environment using the following TOOLS:
        {json.dumps(tools, indent=2)}

        RESPONSE FORMAT:
        You must strictly respond in valid JSON format.
        Structure:
        {{
            "emotion": "one of [calm, reassuring, concerned, neutral]",
            "voice_response": "The spoken words to the patient (keep it short and simple).",
            "function_call": {{ "name": "function_name", "arguments": {{...}} }} (OPTIONAL, only if action needed)
        }}

        Example 1 (Conversation):
        {{
            "emotion": "reassuring",
            "voice_response": "I am here with you. It is 3 PM, time for tea.",
            "function_call": null
        }}

        Example 2 (Action):
        {{
            "emotion": "calm",
            "voice_response": "I will play some relaxing music for you.",
            "function_call": {{ "name": "open_youtube", "arguments": {{}} }}
        }}

        Do NOT output markdown. Do NOT output plain text. ONLY JSON.
        """

    def process_input(self, user_text):
        self._init_resources()
        
        # 1. Retrieve Context
        context_str = ""
        try:
            mems = self.memory.retrieve_relevant(user_text)
            context_str += "\n[Memory]: " + "; ".join(mems)
            
            vedic = self.ayurveda.retrieve(user_text)
            context_str += "\n[Ayurveda]: " + "; ".join(vedic)
        except Exception as e:
            print(f"[Warning] Context retrieval failed: {e}")

        # 2. Call LLM
        full_prompt = f"""
        Context: {context_str}
        
        Patient says: "{user_text}"
        
        Respond in JSON:
        """
        
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': full_prompt},
            ])
            raw_content = response['message']['content']
            
            # 3. Parse JSON
            # Clean up potential markdown blocks ```json ... ```
            clean_content = raw_content.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_content)
            
            # Log interaction
            self.memory.add_memory(f"User: {user_text}")
            self.memory.add_memory(f"ELDA: {parsed.get('voice_response', '')}")
            
            return parsed
            
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM: {raw_content}")
            # Fallback
            return {
                "emotion": "neutral",
                "voice_response": "I am having trouble understanding, but I am here.",
                "function_call": None
            }
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "emotion": "concerned",
                "voice_response": "I sense an error, but I am staying with you.",
                "function_call": None
            }

elda_llm = LLMAgent()
