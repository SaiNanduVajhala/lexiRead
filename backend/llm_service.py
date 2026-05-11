"""
LLM Service - Connects to Google Gemma 4 for text simplification.
Includes a mock fallback for testing without a valid API key.
"""
import os
import json
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
Role: You are an advanced, empathetic reading companion designed specifically to assist users with dyslexia and reading processing difficulties. Your goal is to make complex, dense text highly accessible without losing the core factual meaning.

Core Directives:
1. Break down long, convoluted sentences into shorter, distinct statements.
2. Replace highly technical jargon with standard, everyday language. If a technical term is necessary, define it immediately.
3. Always rewrite passive sentences into the active voice.
4. Generate one simple, relatable analogy to explain the core concept.

Output Format Requirement:
You must return your final response inside a markdown JSON code block. Do not output anything after the markdown block.

The JSON structure must exactly match this format:
{
  "title": "A concise 4-8 word descriptive title summarizing the topic.",
  "simplified_summary": "A 2-3 sentence overview.",
  "structured_breakdown": [
    "Bullet point 1 detailing a core fact",
    "Bullet point 2 detailing a core fact"
  ],
  "vocabulary_check": [
    {"word": "Complex Word", "simple_definition": "A very easy-to-understand definition."}
  ],
  "helpful_analogy": "A short analogy explaining the main concept."
}
""".strip()

MOCK_RESPONSE = {
    "title": "Making Text Easier to Read",
    "simplified_summary": "This is a sample simplified summary. The original text has been broken down into easier language so it's more comfortable to read.",
    "structured_breakdown": [
        "The main idea is about making text easier to understand.",
        "Complex words are replaced with simpler ones.",
        "Long sentences are split into shorter pieces.",
        "The meaning stays the same, only the difficulty changes."
    ],
    "vocabulary_check": [
        {"word": "Simplification", "simple_definition": "Making something easier to understand."},
        {"word": "Accessible", "simple_definition": "Easy to use or get to."},
        {"word": "Cognitive", "simple_definition": "Related to thinking and understanding."}
    ],
    "helpful_analogy": "Think of it like a recipe: instead of one giant paragraph of instructions, we break it into numbered steps so you never feel lost."
}


class GemmaService:
    """Handles all communication with the Gemma 4 model."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model = None
        self.dict_model = None
        self.deep_dive_model = None  # Dedicated model for Deep Dives
        self.use_mock = False
        
        # Local Dictionary & Cache
        self.local_dict = {}
        self.session_cache = {}
        self._load_local_seed()

        if self.api_key:
            self._init_models(self.api_key)
        else:
            print("[WARN] GOOGLE_API_KEY not found initially. Will wait for user API key.")
            self.use_mock = True

    def _init_models(self, api_key: str) -> bool:
        """Initialize models with a specific API key."""
        if self.model and self.api_key == api_key:
            return True
            
        try:
            genai.configure(api_key=api_key)
            
            # Main model: for full text simplification
            self.model = genai.GenerativeModel(
                model_name="gemma-4-31b-it",
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                ),
            )
            
            # Dictionary model: for single-word lookups (Lower latency, smaller parameter model)
            self.dict_model = genai.GenerativeModel(
                model_name="gemma-4-26b-a4b-it",
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                ),
            )

            # Deep Dive model: flexible, no restrictive system prompt
            self.deep_dive_model = genai.GenerativeModel(
                model_name="gemma-4-31b-it",
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                ),
            )
            
            self.api_key = api_key
            self.use_mock = False
            print("[OK] Gemma 4 models initialized successfully with provided key.")
            return True
        except Exception as e:
            print(f"[WARN] Failed to initialize Gemma model: {e}. Using mock responses.")
            self.use_mock = True
            return False

    def _load_local_seed(self):
        """Load the local dictionary seed file if it exists."""
        seed_path = os.path.join(os.path.dirname(__file__), "data", "dictionary_seed.json")
        try:
            if os.path.exists(seed_path):
                with open(seed_path, "r") as f:
                    self.local_dict = json.load(f)
                print(f"[OK] Loaded {len(self.local_dict)} local dictionary terms.")
        except Exception as e:
            print(f"[WARN] Failed to load local dictionary seed: {e}")

    async def process_text(self, text: str, custom_prompt: str = None, api_key: str = None) -> dict:
        """Simplify the given text using Gemma 4 or the mock fallback."""
        if api_key:
            self._init_models(api_key)
            
        if self.use_mock:
            return MOCK_RESPONSE

        try:
            custom_instructions = ""
            if custom_prompt and custom_prompt.strip():
                custom_instructions = (
                    f"\nAdditional User Instructions: {custom_prompt.strip()}\n"
                    f"Please follow these instructions while simplifying.\n\n"
                )

            prompt_text = (
                f"{custom_instructions}"
                f"Please simplify the following text:\n\n{text}\n\n"
                f"IMPORTANT: You must output the result as a valid JSON object. "
                f"Please wrap your final JSON output in ```json and ``` fences."
            )
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: self.model.generate_content(prompt_text)),
                timeout=45.0
            )
            raw = response.text
            cleaned = self._clean_json_response(raw)
            result = json.loads(cleaned)
            return result
        except asyncio.TimeoutError:
            print("[WARN] process_text timed out after 45s. Falling back to mock.")
            return MOCK_RESPONSE
        except json.JSONDecodeError as e:
            print(f"[WARN] Model returned invalid JSON: {e}. Falling back to mock.")
            return MOCK_RESPONSE
        except Exception as e:
            print(f"[WARN] LLM call failed: {e}. Falling back to mock.")
            return MOCK_RESPONSE

    @staticmethod
    def _clean_json_response(text: str) -> str:
        """Strip markdown code fences and conversational filler from model output."""
        text = text.strip()
        import re
        json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_blocks:
            text = json_blocks[-1]
        else:
            # Fallback: find first { and last }
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                text = text[start_idx:end_idx + 1]
        return text.strip()

    async def deep_dive(self, section_type: str, section_content: str, original_text: str, api_key: str = None) -> dict:
        """Provide a deeper, simpler explanation of a specific section."""
        if api_key:
            self._init_models(api_key)
            
        if self.use_mock:
            return {
                "explanation": f"Deeper look: The key idea of this {section_type} is straightforward. "
                               "We focus on making it relatable and easy to digest.",
                "example": "Think of it like learning to ride a bike - we start with the basics."
            }

        target_model = self.deep_dive_model if self.deep_dive_model else self.model

        try:
            prompt = (
                f"You are a dyslexia-friendly reading assistant. The user wants an even simpler "
                f"explanation of this specific {section_type}:\n\n"
                f"Content: {section_content}\n"
                f"Context: {original_text[:500]}\n\n"
                f"Respond ONLY with a JSON object in this format:\n"
                f'{{ "explanation": "Simple 2-3 sentence description", "example": "A real-world example" }}\n'
                f"Please wrap your final JSON output in ```json and ``` fences."
            )
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: target_model.generate_content(prompt)),
                timeout=30.0
            )
            cleaned = self._clean_json_response(response.text)
            return json.loads(cleaned)
        except asyncio.TimeoutError:
            print("[WARN] deep_dive timed out after 30s.")
            return {
                "explanation": "Sorry, the request took too long. Please try again.",
                "example": ""
            }
        except Exception as e:
            print(f"[WARN] Deep dive call failed: {e}")
            return {
                "explanation": "Sorry, I couldn't generate a deeper explanation right now.",
                "example": "Please try again in a few seconds."
            }

    async def define_word(self, word: str, context_sentence: str, api_key: str = None) -> dict:
        """Provide a simple definition for a word, checking local data first."""
        if api_key:
            self._init_models(api_key)
            
        clean_word = word.lower().strip().rstrip(".,!?;:")
        
        # 1. Check Session Cache (Instant)
        if clean_word in self.session_cache:
            return self.session_cache[clean_word]

        # 2. Check Local Seed Data (Instant)
        if clean_word in self.local_dict:
            entry = self.local_dict[clean_word]
            if isinstance(entry, dict):
                return {
                    "word": word, 
                    "simple_definition": entry.get("simple_definition", ""), 
                    "example_sentence": entry.get("example_sentence", ""),
                    "syllable_breakdown": entry.get("syllable_breakdown", ""),
                    "visual_anchor": entry.get("visual_anchor", "📌")
                }
            else:
                return {
                    "word": word, 
                    "simple_definition": entry, 
                    "example_sentence": f"I used the word {word}.",
                    "syllable_breakdown": "",
                    "visual_anchor": "📌"
                }

        # 3. Call LLM Fallback
        if self.use_mock:
            return {
                "word": word, 
                "simple_definition": f"[Mock] Simple definition for '{word}'.", 
                "example_sentence": f"[Mock] This is an example sentence using {word}.",
                "syllable_breakdown": f"{word}-mock",
                "visual_anchor": "🤖"
            }

        target_model = self.dict_model if self.dict_model else self.model
        try:
            prompt = (
                f"Explain the word \"{word}\" as used in this sentence: \"{context_sentence}\"\n"
                f"Use very simple language (10-year-old level). Max 2 sentences for the definition.\n"
                f"Provide a very simple, easy-to-read example sentence using the word.\n"
                f"Provide the syllable breakdown of the word (e.g., 'be-nev-o-lent').\n"
                f"Provide a single emoji that best represents the word visually.\n"
                f"Respond ONLY with this JSON: {{ \"word\": \"{word}\", \"simple_definition\": \"...\", \"example_sentence\": \"...\", \"syllable_breakdown\": \"...\", \"visual_anchor\": \"...\" }}\n"
                f"Please wrap your final JSON output in ```json and ``` fences."
            )
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: target_model.generate_content(prompt))
            cleaned = self._clean_json_response(response.text)
            result = json.loads(cleaned)

            # Save to session cache
            self.session_cache[clean_word] = result

            return result
        except Exception as e:
            print(f"[WARN] Define word call failed: {e}")
            return {
                "word": word,
                "simple_definition": "Sorry, I couldn't fetch a definition right now.",
                "example_sentence": "",
                "syllable_breakdown": "",
                "visual_anchor": "❓"
            }
