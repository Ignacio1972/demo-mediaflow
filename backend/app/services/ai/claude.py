"""
Claude AI Service
Handles AI-powered text suggestions and improvements
"""
import logging
import re
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from anthropic import AsyncAnthropic
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for Claude AI text generation and suggestions"""

    # Tone instructions for announcements (Spanish)
    TONE_INSTRUCTIONS = {
        "profesional": "Manten un tono formal, serio y confiable. Usa lenguaje corporativo y evita expresiones coloquiales. Se conciso y directo.",
        "entusiasta": "Usa un tono energetico, emocionante y motivador. Incluye expresiones como 'Increible!', 'No te lo pierdas!', 'Aprovecha ahora!'. Transmite emocion y urgencia positiva.",
        "amigable": "Se cercano, calido y acogedor. Habla como si fueras un amigo dando un buen consejo. Usa un lenguaje casual pero respetuoso.",
        "urgente": "Transmite importancia y necesidad de accion inmediata. Usa palabras como 'ATENCION', 'IMPORTANTE', 'ULTIMO MOMENTO', 'AHORA'. Se directo y enfatico.",
        "informativo": "Se claro, objetivo y directo. Presenta los datos de forma organizada sin adornos ni emociones. Enfocate en transmitir informacion precisa."
    }

    # Category-specific contexts
    CATEGORY_CONTEXTS = {
        "ofertas": "Enfocate en el ahorro, descuentos y beneficios. Crea urgencia y emocion por la oferta.",
        "eventos": "Destaca la experiencia unica, la diversion y la importancia de asistir. Menciona fecha y hora si es relevante.",
        "informacion": "Se claro, directo y util. Proporciona la informacion esencial de manera concisa.",
        "servicios": "Resalta la calidad, conveniencia y beneficios del servicio. Invita a la accion.",
        "horarios": "Comunica claramente los horarios, se especifico y menciona cualquier cambio importante.",
        "emergencias": "Se directo, claro y tranquilizador. Proporciona instrucciones especificas si es necesario.",
        "general": "Manten un tono versatil que se adapte a diferentes tipos de mensajes."
    }

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


    async def generate_announcements(
        self,
        context: str,
        category: str = "general",
        tone: str = "profesional",
        duration: int = 10,
        keywords: Optional[List[str]] = None,
        temperature: float = 0.8,
        client_context: Optional[str] = None,
        campaign_instructions: Optional[str] = None,
        mode: str = "normal",
        word_limit: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Generate announcement suggestions using Claude AI

        Args:
            context: Description of what to announce
            category: Announcement category (ofertas, eventos, etc.)
            tone: Message tone (profesional, entusiasta, amigable, urgente, informativo)
            duration: Target duration in seconds
            keywords: Optional keywords to include
            temperature: Creativity level (0-1)
            client_context: Client/business context (system prompt)
            campaign_instructions: Campaign-specific AI instructions (added to prompt)
            mode: "normal" (2 suggestions) or "automatic" (1 suggestion)
            word_limit: [min_words, max_words] for automatic mode

        Returns:
            List of suggestions with metadata
        """
        try:
            # Build prompts
            system_prompt = self._build_announcement_system_prompt(
                category=category,
                tone=tone,
                client_context=client_context,
                campaign_instructions=campaign_instructions
            )

            user_prompt = self._build_announcement_user_prompt(
                context=context,
                duration=duration,
                keywords=keywords,
                mode=mode,
                word_limit=word_limit
            )

            logger.info(f"🤖 Generating announcements: mode={mode}, tone={tone}, category={category}")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Parse response
            raw_text = response.content[0].text.strip()
            suggestions = self._parse_announcement_response(raw_text, mode)

            logger.info(f"✅ Generated {len(suggestions)} announcement suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"❌ Announcement generation failed: {str(e)}", exc_info=True)
            raise

    def _build_announcement_system_prompt(
        self,
        category: str,
        tone: str,
        client_context: Optional[str],
        campaign_instructions: Optional[str] = None
    ) -> str:
        """Build system prompt with client context for announcements"""
        # Base: client context or generic
        if client_context:
            base = f"{client_context}\n\n"
            # Add instruction to respect exact spelling from context
            base += "IMPORTANTE: Respeta EXACTAMENTE la ortografia de los nombres propios, marcas y palabras especiales mencionadas arriba. "
            base += "Si un nombre tiene acentos o mayusculas especificas (ej: TÉJA Márket), DEBES escribirlo exactamente asi para que el TTS lo pronuncie correctamente.\n\n"
        else:
            base = "Eres un experto en crear anuncios comerciales efectivos y atractivos para negocios locales.\n\n"

        # General instructions
        base += "Genera anuncios concisos, claros y atractivos en espanol chileno. Respeta estrictamente el limite de palabras indicado. "

        # Tone instruction
        tone_instruction = self.TONE_INSTRUCTIONS.get(tone, self.TONE_INSTRUCTIONS["profesional"])
        base += f"{tone_instruction} "

        # Avoid emojis
        base += "Evita usar emojis o caracteres especiales. "

        # Category instruction
        category_instruction = self.CATEGORY_CONTEXTS.get(category, self.CATEGORY_CONTEXTS["general"])
        base += category_instruction

        # Campaign-specific instructions (added at the end for highest priority)
        if campaign_instructions:
            base += f"\n\n## Instrucciones especificas de la campana:\n{campaign_instructions}"

        return base

    def _duration_to_word_limits(self, duration: int) -> tuple[int, int]:
        """
        Convert duration in seconds to word limits.

        TTS typically reads at 2-3 words per second.
        We use 2 words/sec for min and 3 words/sec for max.
        """
        min_words = duration * 2
        max_words = duration * 3
        return min_words, max_words

    def _build_announcement_user_prompt(
        self,
        context: str,
        duration: int,
        keywords: Optional[List[str]],
        mode: str,
        word_limit: Optional[List[int]]
    ) -> str:
        """Build user prompt based on mode"""
        if mode == "automatic":
            # Automatic mode: 1 suggestion with specific limits
            min_words = word_limit[0] if word_limit else 15
            max_words = word_limit[1] if word_limit else 35

            prompt = f"Mejora este mensaje para un anuncio de radio:\n\n"
            prompt += f"Mensaje original: {context}\n\n"
            prompt += f"IMPORTANTE: Tu respuesta debe ser UN SOLO anuncio de EXACTAMENTE entre {min_words} y {max_words} palabras. "
            prompt += "Se claro, directo y atractivo. "
            prompt += "No incluyas explicaciones, solo el texto del anuncio. "
            prompt += "CUENTA LAS PALABRAS y asegurate de cumplir el limite."
            return prompt

        # Normal mode: 2 options with word limits based on duration
        min_words, max_words = self._duration_to_word_limits(duration)

        prompt = "Genera 2 opciones diferentes de anuncios para lo siguiente:\n\n"
        prompt += f"Contexto: {context}\n"

        if keywords:
            prompt += f"Palabras clave a incluir: {', '.join(keywords)}\n"

        prompt += f"\nREQUISITO DE LONGITUD: Cada anuncio debe tener entre {min_words} y {max_words} palabras "
        prompt += f"(equivalente a {duration} segundos de audio).\n"
        prompt += "\nFormato de respuesta: Proporciona exactamente 2 opciones numeradas, "
        prompt += "cada una en un parrafo separado. No incluyas titulos ni explicaciones adicionales. "
        prompt += "CUENTA LAS PALABRAS de cada opcion para asegurar que cumplan el limite."

        return prompt

    def _parse_announcement_response(self, text: str, mode: str) -> List[Dict]:
        """Parse Claude response into structured suggestions"""
        suggestions = []

        if mode == "automatic":
            # Automatic mode: single suggestion
            cleaned = text.strip()
            if cleaned:
                suggestions.append({
                    "id": f"sug_{uuid.uuid4().hex[:8]}",
                    "text": cleaned,
                    "char_count": len(cleaned),
                    "word_count": len(cleaned.split()),
                    "created_at": datetime.now().isoformat()
                })
            return suggestions

        # Normal mode: find 2 numbered suggestions
        patterns = [
            r'(\d+)[.\)]\s*(.+?)(?=\d+[.\)]|$)',  # 1. text or 1) text
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for _, match in matches:
                cleaned = match.strip()
                if cleaned and len(cleaned) > 20:
                    suggestions.append({
                        "id": f"sug_{uuid.uuid4().hex[:8]}",
                        "text": cleaned,
                        "char_count": len(cleaned),
                        "word_count": len(cleaned.split()),
                        "created_at": datetime.now().isoformat()
                    })
            if len(suggestions) >= 2:
                break

        # Fallback: split by paragraphs
        if len(suggestions) < 2:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 20]
            for para in paragraphs:
                if len(suggestions) >= 2:
                    break
                # Remove numbering if present
                para = re.sub(r'^\d+[.\)]\s*', '', para)
                if not any(s['text'] == para for s in suggestions):
                    suggestions.append({
                        "id": f"sug_{uuid.uuid4().hex[:8]}",
                        "text": para,
                        "char_count": len(para),
                        "word_count": len(para.split()),
                        "created_at": datetime.now().isoformat()
                    })

        return suggestions[:2]


# Singleton instance
claude_service = ClaudeService()
