"""
RecoverOps AI — LLM Engine
Generates personalized dunning messages using OpenAI.
Falls back to templates if API key is unavailable.
"""

from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()


class LLMEngine:
    """
    Uses OpenAI to generate personalized recovery messages.
    Gracefully degrades to templates when no API key is set.
    """

    def __init__(self):
        self.client = None
        if settings.openai_api_key and settings.openai_api_key != "sk-xxxxxxxxxxxxxxxxxxxxxxxx":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                self.client = None

    def generate_dunning_message(
        self,
        customer_name: str,
        amount: float,
        failure_reason: str,
        channel: str = "whatsapp",
        language: str = "en",
    ) -> str:
        """Generate a personalized dunning message."""
        if self.client is None:
            return self._template_message(amount, failure_reason)

        try:
            prompt = (
                f"Write a short, friendly {channel} message in {language} "
                f"to {customer_name} about their failed payment of ₹{amount:,.2f}. "
                f"Reason: {failure_reason}. "
                f"Keep it under 50 words. Include one emoji. "
                f"Do NOT include any links or placeholders."
            )

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a payment recovery assistant for an Indian fintech company."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()
        except Exception:
            return self._template_message(amount, failure_reason)

    def _template_message(self, amount: float, reason: str) -> str:
        """Fallback template messages."""
        templates = {
            "insufficient_funds": f"Hi! Your ₹{amount:,.2f} payment failed due to low balance. Your order is reserved. Complete payment anytime in 24 hrs! 🙏",
            "card_expired": f"Hello! Your card seems expired. Please update payment method for ₹{amount:,.2f} order. Cart saved! 💳",
            "authentication_failed": f"Hi! OTP verification failed for ₹{amount:,.2f}. Keep OTP ready and retry now! 🔐",
            "bank_technical": f"Hi! Bank issue resolved. Complete your ₹{amount:,.2f} payment now! ⚡",
        }
        return templates.get(
            reason,
            f"Hi! Your ₹{amount:,.2f} payment is pending. Complete it now! 🛒",
        )


# Singleton
llm_engine = LLMEngine()