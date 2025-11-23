"""
Claude AI Service
Handles AI-powered text suggestions and improvements
"""
import logging
from typing import Optional, Dict, List
from anthropic import AsyncAnthropic
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for Claude AI text generation and suggestions"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL

    async def generate_suggestion(
        self,
        prompt: str,
        tone: str = "professional",
        max_words: int = 30,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate AI suggestion for message text

        Args:
            prompt: User's initial idea or topic
            tone: Tone of voice (professional, casual, urgent, friendly)
            max_words: Maximum words in suggestion
            context: Optional business/client context

        Returns:
            str: AI-generated suggestion
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(tone, max_words, context)

        try:
            logger.info(
                f"🤖 Generating AI suggestion: tone={tone}, max_words={max_words}"
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            suggestion = response.content[0].text.strip()

            logger.info(f"✅ AI suggestion generated: {len(suggestion)} chars")
            return suggestion

        except Exception as e:
            logger.error(f"❌ AI suggestion failed: {str(e)}", exc_info=True)
            raise

    async def generate_multiple_suggestions(
        self,
        prompt: str,
        tone: str = "professional",
        max_words: int = 30,
        context: Optional[str] = None,
        count: int = 3,
    ) -> List[str]:
        """
        Generate multiple AI suggestions for message text

        Args:
            prompt: User's initial idea or topic
            tone: Tone of voice (professional, casual, urgent, friendly)
            max_words: Maximum words in suggestion
            context: Optional business/client context
            count: Number of suggestions to generate (1-5)

        Returns:
            List[str]: List of AI-generated suggestions
        """
        count = min(max(count, 1), 5)  # Limit 1-5

        # Build system prompt for multiple suggestions
        system_prompt = self._build_system_prompt_multiple(tone, max_words, context, count)

        try:
            logger.info(
                f"🤖 Generating {count} AI suggestions: tone={tone}, max_words={max_words}"
            )

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=600,
                temperature=0.8,  # Higher temperature for variety
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            suggestions_text = response.content[0].text.strip()

            # Split by newlines and clean up
            suggestions = [
                s.strip().lstrip('123456789.-) ')
                for s in suggestions_text.split("\n")
                if s.strip() and not s.strip().startswith('#')
            ]

            # Filter out empty and ensure we have the right count
            suggestions = [s for s in suggestions if len(s) > 10][:count]

            logger.info(f"✅ Generated {len(suggestions)} suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"❌ AI suggestions generation failed: {str(e)}", exc_info=True)
            raise

    async def improve_text(
        self,
        text: str,
        tone: Optional[str] = None,
        max_words: Optional[int] = None,
    ) -> str:
        """
        Improve existing text

        Args:
            text: Text to improve
            tone: Optional tone adjustment
            max_words: Optional word limit

        Returns:
            str: Improved text
        """
        system_prompt = f"""Eres un experto en comunicación para mensajes de audio comerciales.
Mejora el siguiente texto manteniendo su mensaje principal.
"""

        if tone:
            system_prompt += f"\nTono deseado: {tone}"

        if max_words:
            system_prompt += f"\nMáximo {max_words} palabras."

        system_prompt += "\n\nDevuelve solo el texto mejorado, sin explicaciones."

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.5,
                system=system_prompt,
                messages=[{"role": "user", "content": text}],
            )

            improved = response.content[0].text.strip()
            logger.info(f"✅ Text improved: {len(text)} → {len(improved)} chars")

            return improved

        except Exception as e:
            logger.error(f"❌ Text improvement failed: {str(e)}", exc_info=True)
            raise

    async def generate_variations(
        self, text: str, count: int = 3, tone: Optional[str] = None
    ) -> List[str]:
        """
        Generate multiple variations of a text

        Args:
            text: Original text
            count: Number of variations (1-5)
            tone: Optional tone

        Returns:
            List[str]: List of variations
        """
        count = min(max(count, 1), 5)  # Limit 1-5

        system_prompt = f"""Eres un experto en comunicación comercial.
Genera {count} variaciones diferentes del siguiente mensaje.
Mantén el mensaje principal pero varía el estilo y palabras.
"""

        if tone:
            system_prompt += f"\nTono: {tone}"

        system_prompt += f"\n\nDevuelve SOLO las {count} variaciones, una por línea, sin numeración."

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=400,
                temperature=0.9,
                system=system_prompt,
                messages=[{"role": "user", "content": text}],
            )

            variations_text = response.content[0].text.strip()
            variations = [
                v.strip() for v in variations_text.split("\n") if v.strip()
            ]

            logger.info(f"✅ Generated {len(variations)} variations")
            return variations[:count]

        except Exception as e:
            logger.error(f"❌ Variations generation failed: {str(e)}", exc_info=True)
            raise

    def _build_system_prompt(
        self, tone: str, max_words: int, context: Optional[str]
    ) -> str:
        """Build system prompt for AI generation"""

        prompt = f"""Eres un experto en crear mensajes de audio comerciales efectivos para sistemas TTS.

Tu tarea es generar mensajes claros, concisos y profesionales.

Características del mensaje:
- Tono: {tone}
- Máximo: {max_words} palabras
- Idioma: Español
- Formato: Mensaje directo sin saludo ni despedida
- Estilo: Claro, natural, fácil de pronunciar por TTS
"""

        if context:
            prompt += f"\n\nContexto del negocio:\n{context}"

        prompt += """

IMPORTANTE:
- Devuelve SOLO el mensaje, sin comillas ni explicaciones
- Evita signos de puntuación complejos
- Usa lenguaje natural y directo
- Piensa en cómo sonará al ser leído por una voz sintética
"""

        return prompt

    def _build_system_prompt_multiple(
        self, tone: str, max_words: int, context: Optional[str], count: int
    ) -> str:
        """Build system prompt for generating multiple suggestions"""

        prompt = f"""Eres un experto en crear mensajes de audio comerciales efectivos para sistemas TTS.

Tu tarea es generar {count} mensajes diferentes para la misma idea.

Características de cada mensaje:
- Tono: {tone}
- Máximo: {max_words} palabras
- Idioma: Español
- Formato: Mensaje directo sin saludo ni despedida
- Estilo: Claro, natural, fácil de pronunciar por TTS
"""

        if context:
            prompt += f"\n\nContexto del negocio:\n{context}"

        prompt += f"""

IMPORTANTE:
- Devuelve EXACTAMENTE {count} mensajes diferentes, uno por línea
- NO uses numeración, bullets, ni comillas
- Cada mensaje debe ser una variación única con diferentes palabras
- Evita signos de puntuación complejos
- Usa lenguaje natural y directo
- Piensa en cómo sonará al ser leído por una voz sintética
- Mantén cada mensaje en {max_words} palabras o menos

Formato esperado:
Mensaje uno aquí
Mensaje dos aquí
Mensaje tres aquí
"""

        return prompt


# Singleton instance
claude_service = ClaudeService()
