"""
app/services/llm_service.py
Augmented prompt builder and LLM answer generator.
Supports Gemini, OpenAI, and a zero-dependency offline synthesis mode.
"""

from typing import List
import urllib.request
import json
from app.config import settings
from app.models.schemas import SourceChunk


def build_augmented_prompt(query: str, sources: List[SourceChunk]) -> str:
    """
    Combines the user query with the retrieved source snippets into an augmented prompt.
    """
    context_text = "\n\n".join(
        [f"[Source {idx+1}: {s.document_title}]\n{s.text}" for idx, s in enumerate(sources)]
    )
    
    prompt = f"""You are a helpful and precise knowledge assistant.
Answer the user's question based strictly on the provided Context below.
If the answer cannot be determined from the context, state that the information is not available in the knowledge base.

=== CONTEXT ===
{context_text}

=== QUESTION ===
{query}

=== ANSWER ===
"""
    return prompt


class LLMService:
    """Service to handle generation via external LLM or local fallback."""

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY

    def generate_answer(self, query: str, sources: List[SourceChunk]) -> str:
        """
        Determines available provider and returns generated answer.
        """
        if not sources:
            return "I could not find any relevant information in the knowledge base to answer your question."

        # 1. If Gemini API key is configured
        if self.gemini_key:
            return self._call_gemini(query, sources)


        # 3. Offline / Demo Mode (No API keys needed)
        return self._offline_generator(query, sources)

    def _offline_generator(self, query: str, sources: List[SourceChunk]) -> str:
        """
        Simulates generation for zero-credential offline learning.
        Extracts and synthesizes the most relevant statements from retrieved chunks.
        """
        best_source = sources[0]
        summary_lines = [
            f"Based on '{best_source.document_title}':",
            f"• {best_source.text.strip()}"
        ]
        if len(sources) > 1:
            summary_lines.append(f"\nAdditional context from '{sources[1].document_title}':")
            summary_lines.append(f"• {sources[1].text.strip()}")
            
        return "\n".join(summary_lines)

    def _call_gemini(self, query: str, sources: List[SourceChunk]) -> str:
        """Calls Google Gemini API using Python's standard urllib (no extra library needed)."""
        prompt = build_augmented_prompt(query, sources)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error communicating with Gemini API: {str(e)}"

    def _call_openai(self, query: str, sources: List[SourceChunk]) -> str:
        """Calls OpenAI Chat Completions API using standard urllib."""
        prompt = build_augmented_prompt(query, sources)
        url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful knowledge assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}"
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error communicating with OpenAI API: {str(e)}"


llm_service = LLMService()