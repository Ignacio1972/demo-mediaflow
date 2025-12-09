# Sistema de IA y Claude - Documentaci贸n de Implementaci贸n

**Prop贸sito**: Documentaci贸n completa para replicar el sistema de inteligencia artificial del sistema legacy en MediaFlow v2.

---

## 1. Resumen del Sistema Legacy

El sistema legacy tiene un m贸dulo completo de IA que permite:

1. **Gesti贸n de Clientes/Contextos** - Sistema multi-tenant donde cada cliente tiene un contexto de IA personalizado
2. **Generaci贸n de Anuncios con Claude** - Genera 2 sugerencias de texto basadas en contexto y par谩metros
3. **Modo Autom谩tico** - Generaci贸n simplificada con l铆mites de palabras din谩micos
4. **Panel de Administraci贸n** - UI para gestionar clientes y contextos
5. **Integraci贸n con Dashboard** - Componente AISuggestions en el dashboard principal

---

## 2. Arquitectura del Sistema Legacy

```
猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬傗攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬傗攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬      FRONTEND (claude.html / Dashboard)        猬傗        API         猬
猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬                                                 猬                      猬
猬  猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬  猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬 猬  claude-service.php  猬
猬  猬 Selector de Cliente    猬  猬 Config Panel   猬 猬傗攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬  猬 - Dropdown clientes    猬  猬 - Contexto     猬 猬  - Genera anuncios    猬
猬  猬 - Preview contexto     猬  猬 - Tono         猬 猬  - Llama Claude API    猬
猬  猬 - Bot贸n "Activo"       猬  猬 - Duraci贸n     猬 猬  - Parsea respuesta    猬
猬  猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬  猬 - Creatividad  猬 猬  - Guarda m茅tricas    猬
猬                                猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬 猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬  猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬    猬                      猬
猬  猬      Panel de Sugerencias Generadas        猬    猬  clients-service.php 猬
猬  猬  - Muestra 2 sugerencias                   猬    猬傗攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬  猬  - Contador palabras/caracteres            猬    猬  - CRUD clientes      猬
猬  猬  - Bot贸n "Usar" (env铆a al TTS)             猬    猬  - Cliente activo     猬
猬  猬  - Bot贸n "Copiar"                          猬    猬  - Contextos IA       猬
猬  猬  - Estad铆sticas: modelo, tokens, costo     猬    猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
猬  猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬    猬                      猬
猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬斺攢猬
```

---

## 3. Componentes a Implementar en MediaFlow v2

### 3.1 Sistema de Clientes/Contextos (NUEVO - No existe en v2)

**Prop贸sito**: Permitir configurar diferentes contextos de IA seg煤n el cliente/negocio activo.

#### Modelo de Datos: `AIClient`

```python
# backend/app/models/ai_client.py

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class AIClient(Base):
    """Modelo para clientes/contextos de IA"""
    __tablename__ = "ai_clients"

    id = Column(String(50), primary_key=True)  # ej: "casa_costanera", "mall_plaza"
    name = Column(String(100), nullable=False)  # Nombre display
    context = Column(Text, nullable=False)  # Contexto para Claude (system prompt)
    category = Column(String(50), default="general")  # Tipo de negocio
    active = Column(Boolean, default=True)  # Si est谩 disponible
    is_default = Column(Boolean, default=False)  # Cliente por defecto del sistema

    # Configuraciones adicionales (opcional)
    settings = Column(JSON, nullable=True)  # {default_tone, language, max_length, keywords}
    custom_prompts = Column(JSON, nullable=True)  # Prompts por categor铆a

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### Schema Pydantic

```python
# backend/app/schemas/ai_client.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class AIClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    context: str = Field(..., min_length=10, max_length=5000)
    category: str = Field(default="general", max_length=50)
    active: bool = True
    settings: Optional[Dict] = None
    custom_prompts: Optional[Dict[str, str]] = None

class AIClientCreate(AIClientBase):
    id: Optional[str] = None  # Auto-generado si no se provee

class AIClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    context: Optional[str] = Field(None, min_length=10, max_length=5000)
    category: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None
    settings: Optional[Dict] = None
    custom_prompts: Optional[Dict[str, str]] = None

class AIClientResponse(AIClientBase):
    id: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AIClientListResponse(BaseModel):
    clients: List[AIClientResponse]
    active_client_id: Optional[str]
    total: int
```

---

### 3.2 Endpoints de Clientes IA

```python
# backend/app/api/v1/endpoints/settings/ai_clients.py

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.ai_client import (
    AIClientCreate, AIClientUpdate, AIClientResponse, AIClientListResponse
)
from app.services.ai.client_manager import ai_client_manager

router = APIRouter()

@router.get("", response_model=AIClientListResponse)
async def list_clients(db: AsyncSession = Depends(get_db)):
    """Listar todos los clientes IA"""
    clients = await ai_client_manager.list_clients(db)
    active_id = await ai_client_manager.get_active_client_id(db)
    return AIClientListResponse(
        clients=clients,
        active_client_id=active_id,
        total=len(clients)
    )

@router.get("/active", response_model=AIClientResponse)
async def get_active_client(db: AsyncSession = Depends(get_db)):
    """Obtener cliente activo actual"""
    client = await ai_client_manager.get_active_client(db)
    if not client:
        raise HTTPException(status_code=404, detail="No hay cliente activo configurado")
    return client

@router.post("/active/{client_id}")
async def set_active_client(client_id: str, db: AsyncSession = Depends(get_db)):
    """Establecer cliente como activo del sistema"""
    success = await ai_client_manager.set_active_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"success": True, "active_client_id": client_id}

@router.get("/{client_id}", response_model=AIClientResponse)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)):
    """Obtener un cliente espec铆fico"""
    client = await ai_client_manager.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.post("", response_model=AIClientResponse, status_code=201)
async def create_client(data: AIClientCreate, db: AsyncSession = Depends(get_db)):
    """Crear nuevo cliente IA"""
    client = await ai_client_manager.create_client(db, data)
    return client

@router.patch("/{client_id}", response_model=AIClientResponse)
async def update_client(
    client_id: str,
    data: AIClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar cliente existente"""
    client = await ai_client_manager.update_client(db, client_id, data)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.delete("/{client_id}")
async def delete_client(client_id: str, db: AsyncSession = Depends(get_db)):
    """Eliminar cliente (no puede ser el activo ni el 煤nico)"""
    success, error = await ai_client_manager.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=400, detail=error)
    return {"success": True, "message": "Cliente eliminado"}
```

---

### 3.3 Servicio de Gesti贸n de Clientes IA

```python
# backend/app/services/ai/client_manager.py

import logging
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
import time

from app.models.ai_client import AIClient
from app.schemas.ai_client import AIClientCreate, AIClientUpdate

logger = logging.getLogger(__name__)

class AIClientManager:
    """Servicio para gestionar clientes/contextos de IA"""

    async def list_clients(self, db: AsyncSession) -> List[AIClient]:
        """Listar todos los clientes"""
        result = await db.execute(
            select(AIClient).where(AIClient.active == True).order_by(AIClient.name)
        )
        return result.scalars().all()

    async def get_client(self, db: AsyncSession, client_id: str) -> Optional[AIClient]:
        """Obtener cliente por ID"""
        result = await db.execute(
            select(AIClient).where(AIClient.id == client_id)
        )
        return result.scalar_one_or_none()

    async def get_active_client(self, db: AsyncSession) -> Optional[AIClient]:
        """Obtener el cliente marcado como activo (is_default=True)"""
        result = await db.execute(
            select(AIClient).where(AIClient.is_default == True)
        )
        client = result.scalar_one_or_none()

        # Fallback: primer cliente activo
        if not client:
            result = await db.execute(
                select(AIClient).where(AIClient.active == True).limit(1)
            )
            client = result.scalar_one_or_none()

        return client

    async def get_active_client_id(self, db: AsyncSession) -> Optional[str]:
        """Obtener solo el ID del cliente activo"""
        client = await self.get_active_client(db)
        return client.id if client else None

    async def set_active_client(self, db: AsyncSession, client_id: str) -> bool:
        """Establecer cliente como el activo del sistema"""
        # Verificar que existe
        client = await self.get_client(db, client_id)
        if not client:
            return False

        # Quitar is_default de todos
        await db.execute(
            update(AIClient).values(is_default=False)
        )

        # Establecer nuevo default
        await db.execute(
            update(AIClient)
            .where(AIClient.id == client_id)
            .values(is_default=True)
        )

        await db.commit()
        logger.info(f"Cliente activo cambiado a: {client_id}")
        return True

    async def create_client(
        self, db: AsyncSession, data: AIClientCreate
    ) -> AIClient:
        """Crear nuevo cliente"""
        # Generar ID si no se provee
        client_id = data.id or f"custom_{int(time.time())}"

        client = AIClient(
            id=client_id,
            name=data.name,
            context=data.context,
            category=data.category,
            active=data.active,
            settings=data.settings,
            custom_prompts=data.custom_prompts
        )

        db.add(client)
        await db.commit()
        await db.refresh(client)

        logger.info(f"Cliente IA creado: {client_id}")
        return client

    async def update_client(
        self, db: AsyncSession, client_id: str, data: AIClientUpdate
    ) -> Optional[AIClient]:
        """Actualizar cliente existente"""
        client = await self.get_client(db, client_id)
        if not client:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        await db.commit()
        await db.refresh(client)

        logger.info(f"Cliente IA actualizado: {client_id}")
        return client

    async def delete_client(
        self, db: AsyncSession, client_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Eliminar cliente con validaciones"""
        client = await self.get_client(db, client_id)
        if not client:
            return False, "Cliente no encontrado"

        # No eliminar si es el activo
        if client.is_default:
            return False, "No se puede eliminar el cliente activo"

        # No eliminar si es el 煤nico
        result = await db.execute(select(AIClient).where(AIClient.active == True))
        count = len(result.scalars().all())
        if count <= 1:
            return False, "Debe existir al menos un cliente"

        await db.delete(client)
        await db.commit()

        logger.info(f"Cliente IA eliminado: {client_id}")
        return True, None

# Singleton
ai_client_manager = AIClientManager()
```

---

### 3.4 Servicio Claude Mejorado (Actualizar el existente)

```python
# backend/app/services/ai/claude.py (ACTUALIZADO)

"""
Claude AI Service - Mejorado con soporte de contextos de cliente
"""
import logging
from typing import Optional, Dict, List
from anthropic import AsyncAnthropic
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for Claude AI text generation with client context support"""

    # Definici贸n de tonos disponibles
    TONE_INSTRUCTIONS = {
        "profesional": "Mant茅n un tono formal, serio y confiable. Usa lenguaje corporativo y evita expresiones coloquiales. S茅 conciso y directo.",
        "entusiasta": "Usa un tono energ茅tico, emocionante y motivador. Incluye expresiones como '隆Incre铆ble!', '隆No te lo pierdas!', '隆Aprovecha ahora!'. Transmite emoci贸n y urgencia positiva.",
        "amigable": "S茅 cercano, c谩lido y acogedor. Habla como si fueras un amigo dando un buen consejo. Usa un lenguaje casual pero respetuoso.",
        "urgente": "Transmite importancia y necesidad de acci贸n inmediata. Usa palabras como 'ATENCI脫N', 'IMPORTANTE', '脷LTIMO MOMENTO', 'AHORA'. S茅 directo y enf谩tico.",
        "informativo": "S茅 claro, objetivo y directo. Presenta los datos de forma organizada sin adornos ni emociones. Enf贸cate en transmitir informaci贸n precisa."
    }

    # Contextos por categor铆a
    CATEGORY_CONTEXTS = {
        "ofertas": "Enf贸cate en el ahorro, descuentos y beneficios. Crea urgencia y emoci贸n por la oferta.",
        "eventos": "Destaca la experiencia 煤nica, la diversi贸n y la importancia de asistir. Menciona fecha y hora si es relevante.",
        "informacion": "S茅 claro, directo y 煤til. Proporciona la informaci贸n esencial de manera concisa.",
        "servicios": "Resalta la calidad, conveniencia y beneficios del servicio. Invita a la acci贸n.",
        "horarios": "Comunica claramente los horarios, s茅 espec铆fico y menciona cualquier cambio importante.",
        "emergencias": "S茅 directo, claro y tranquilizador. Proporciona instrucciones espec铆ficas si es necesario.",
        "general": "Mant茅n un tono vers谩til que se adapte a diferentes tipos de mensajes."
    }

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS

    async def generate_announcements(
        self,
        context: str,
        category: str = "general",
        tone: str = "profesional",
        duration: int = 10,
        keywords: Optional[List[str]] = None,
        temperature: float = 0.8,
        client_context: Optional[str] = None,
        mode: str = "normal",
        word_limit: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Genera sugerencias de anuncios usando Claude AI

        Args:
            context: Descripci贸n de lo que se quiere anunciar
            category: Categor铆a del anuncio (ofertas, eventos, etc.)
            tone: Tono del mensaje
            duration: Duraci贸n objetivo en segundos
            keywords: Palabras clave opcionales
            temperature: Creatividad (0-1)
            client_context: Contexto del cliente/negocio
            mode: "normal" (2 sugerencias) o "automatic" (1 sugerencia)
            word_limit: [min_words, max_words] para modo autom谩tico

        Returns:
            Lista de sugerencias con metadata
        """
        try:
            # Construir system prompt
            system_prompt = self._build_system_prompt(
                category=category,
                tone=tone,
                client_context=client_context
            )

            # Construir user prompt
            user_prompt = self._build_user_prompt(
                context=context,
                duration=duration,
                keywords=keywords,
                mode=mode,
                word_limit=word_limit
            )

            logger.info(f"Generando anuncios: mode={mode}, tone={tone}, category={category}")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Parsear respuesta
            raw_text = response.content[0].text.strip()
            suggestions = self._parse_response(raw_text, mode)

            logger.info(f"Generadas {len(suggestions)} sugerencias")

            return suggestions

        except Exception as e:
            logger.error(f"Error generando anuncios: {e}", exc_info=True)
            raise

    def _build_system_prompt(
        self,
        category: str,
        tone: str,
        client_context: Optional[str]
    ) -> str:
        """Construir system prompt con contexto de cliente"""

        # Base del prompt (contexto del cliente o gen茅rico)
        if client_context:
            base = f"{client_context} "
        else:
            base = "Eres un experto en crear anuncios comerciales efectivos y atractivos para negocios locales. "

        # Instrucciones generales
        base += "Genera anuncios cortos (m谩ximo 100 palabras), claros y atractivos en espa帽ol chileno. "

        # Instrucci贸n de tono
        tone_instruction = self.TONE_INSTRUCTIONS.get(tone, self.TONE_INSTRUCTIONS["profesional"])
        base += f"{tone_instruction} "

        # Evitar emojis
        base += "Evita usar emojis o caracteres especiales. "

        # Instrucci贸n de categor铆a
        category_instruction = self.CATEGORY_CONTEXTS.get(category, self.CATEGORY_CONTEXTS["general"])
        base += category_instruction

        return base

    def _build_user_prompt(
        self,
        context: str,
        duration: int,
        keywords: Optional[List[str]],
        mode: str,
        word_limit: Optional[List[int]]
    ) -> str:
        """Construir user prompt seg煤n el modo"""

        if mode == "automatic":
            # Modo autom谩tico: 1 sugerencia con l铆mites espec铆ficos
            min_words = word_limit[0] if word_limit else 15
            max_words = word_limit[1] if word_limit else 35

            prompt = f"Mejora este mensaje para un anuncio de radio:\n\n"
            prompt += f"Mensaje original: {context}\n\n"
            prompt += f"IMPORTANTE: Tu respuesta debe ser UN SOLO anuncio de EXACTAMENTE entre {min_words} y {max_words} palabras. "
            prompt += "S茅 claro, directo y atractivo. "
            prompt += "No incluyas explicaciones, solo el texto del anuncio. "
            prompt += "CUENTA LAS PALABRAS y aseg煤rate de cumplir el l铆mite."

            return prompt

        # Modo normal: 2 opciones
        prompt = "Genera 2 opciones diferentes de anuncios para lo siguiente:\n\n"
        prompt += f"Contexto: {context}\n"

        if keywords:
            prompt += f"Palabras clave a incluir: {', '.join(keywords)}\n"

        prompt += f"Duraci贸n aproximada al leer: {duration} segundos\n"
        prompt += "\nFormato de respuesta: Proporciona exactamente 2 opciones numeradas, "
        prompt += "cada una en un p谩rrafo separado. No incluyas t铆tulos ni explicaciones adicionales."

        return prompt

    def _parse_response(self, text: str, mode: str) -> List[Dict]:
        """Parsear respuesta de Claude en sugerencias estructuradas"""
        import uuid
        from datetime import datetime

        suggestions = []

        if mode == "automatic":
            # Modo autom谩tico: solo 1 sugerencia
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

        # Modo normal: buscar 2 sugerencias
        # Patrones para encontrar sugerencias numeradas
        import re

        patterns = [
            r'\d+\.\s*(.+?)(?=\d+\.|$)',  # 1. texto
            r'\d+\)\s*(.+?)(?=\d+\)|$)',   # 1) texto
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
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

        # Fallback: dividir por p谩rrafos
        if len(suggestions) < 2:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 20]
            for para in paragraphs:
                if len(suggestions) >= 2:
                    break
                # Evitar duplicados
                if not any(s['text'] == para for s in suggestions):
                    suggestions.append({
                        "id": f"sug_{uuid.uuid4().hex[:8]}",
                        "text": para,
                        "char_count": len(para),
                        "word_count": len(para.split()),
                        "created_at": datetime.now().isoformat()
                    })

        return suggestions[:2]

    # M茅todos existentes se mantienen igual...
    async def generate_suggestion(self, prompt: str, tone: str = "professional",
                                   max_words: int = 30, context: Optional[str] = None) -> str:
        """M茅todo original para compatibilidad"""
        # ... implementaci贸n existente ...
        pass

    async def improve_text(self, text: str, tone: Optional[str] = None,
                          max_words: Optional[int] = None) -> str:
        """M茅todo existente para mejorar texto"""
        # ... implementaci贸n existente ...
        pass


# Singleton
claude_service = ClaudeService()
```

---

### 3.5 Endpoint de Generaci贸n Mejorado

```python
# backend/app/api/v1/endpoints/ai.py (ACTUALIZADO)

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.ai.claude import claude_service
from app.services.ai.client_manager import ai_client_manager

router = APIRouter()


class GenerateAnnouncementsRequest(BaseModel):
    """Request para generar anuncios estilo legacy"""
    context: str = Field(..., min_length=5, max_length=1000, description="Descripci贸n del anuncio")
    category: str = Field(default="general", description="Categor铆a del anuncio")
    tone: str = Field(default="profesional", description="Tono del mensaje")
    duration: int = Field(default=10, ge=5, le=30, description="Duraci贸n en segundos")
    keywords: Optional[List[str]] = Field(default=None, description="Palabras clave")
    temperature: float = Field(default=0.8, ge=0, le=1, description="Creatividad")
    mode: str = Field(default="normal", pattern="^(normal|automatic)$")
    word_limit: Optional[List[int]] = Field(default=None, description="[min, max] palabras")
    # El contexto del cliente se obtiene autom谩ticamente del cliente activo


class GenerateAnnouncementsResponse(BaseModel):
    success: bool
    suggestions: List[dict]
    model: str
    tokens_used: Optional[int] = None


@router.post(
    "/generate",
    response_model=GenerateAnnouncementsResponse,
    summary="Generar Anuncios con IA",
    description="Genera 2 sugerencias de anuncios usando Claude AI con contexto de cliente"
)
async def generate_announcements(
    request: GenerateAnnouncementsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Genera anuncios usando Claude AI con el contexto del cliente activo.

    Replica la funcionalidad del sistema legacy:
    - Obtiene el contexto del cliente activo autom谩ticamente
    - Genera 2 sugerencias en modo normal, 1 en modo autom谩tico
    - Retorna metadata de cada sugerencia (palabras, caracteres)
    """
    try:
        # Obtener contexto del cliente activo
        active_client = await ai_client_manager.get_active_client(db)
        client_context = active_client.context if active_client else None

        # Generar sugerencias
        suggestions = await claude_service.generate_announcements(
            context=request.context,
            category=request.category,
            tone=request.tone,
            duration=request.duration,
            keywords=request.keywords,
            temperature=request.temperature,
            client_context=client_context,
            mode=request.mode,
            word_limit=request.word_limit
        )

        return GenerateAnnouncementsResponse(
            success=True,
            suggestions=suggestions,
            model=claude_service.model,
            tokens_used=None  # TODO: Obtener de la respuesta
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando anuncios: {str(e)}"
        )
```

---

## 4. Frontend - Componentes Vue

### 4.1 Composable useAISuggestions

```typescript
// frontend/src/composables/useAISuggestions.ts

import { ref, reactive, computed } from 'vue'
import { apiClient } from '@/api/client'

interface Suggestion {
  id: string
  text: string
  char_count: number
  word_count: number
  created_at: string
  edited?: boolean
}

interface GenerateParams {
  context: string
  category?: string
  tone?: string
  duration?: number
  keywords?: string[]
  temperature?: number
  mode?: 'normal' | 'automatic'
  word_limit?: [number, number]
}

export function useAISuggestions() {
  const suggestions = ref<Suggestion[]>([])
  const isGenerating = ref(false)
  const selectedSuggestion = ref<Suggestion | null>(null)
  const lastContext = ref<GenerateParams | null>(null)

  const config = reactive({
    tone: 'profesional',
    duration: 10,
    temperature: 0.8,
    keywords: [] as string[],
    showAdvanced: false
  })

  const hasSuggestions = computed(() => suggestions.value.length > 0)

  async function generate(params: GenerateParams) {
    if (isGenerating.value) return

    isGenerating.value = true
    lastContext.value = params

    try {
      const response = await apiClient.post('/api/v1/ai/generate', {
        context: params.context,
        category: params.category || 'general',
        tone: params.tone || config.tone,
        duration: params.duration || config.duration,
        keywords: params.keywords || config.keywords,
        temperature: params.temperature || config.temperature,
        mode: params.mode || 'normal',
        word_limit: params.word_limit
      })

      if (response.data.success) {
        suggestions.value = response.data.suggestions
        return suggestions.value
      } else {
        throw new Error(response.data.error || 'Error generando sugerencias')
      }
    } catch (error) {
      console.error('[useAISuggestions] Error:', error)
      throw error
    } finally {
      isGenerating.value = false
    }
  }

  function selectSuggestion(id: string) {
    const suggestion = suggestions.value.find(s => s.id === id)
    if (suggestion) {
      selectedSuggestion.value = suggestion
      return suggestion
    }
    return null
  }

  function updateSuggestion(id: string, newText: string) {
    const suggestion = suggestions.value.find(s => s.id === id)
    if (suggestion) {
      suggestion.text = newText
      suggestion.char_count = newText.length
      suggestion.word_count = newText.split(/\s+/).filter(w => w).length
      suggestion.edited = true
    }
  }

  function clearSuggestions() {
    suggestions.value = []
    selectedSuggestion.value = null
    lastContext.value = null
  }

  async function regenerateSuggestion(id: string) {
    if (!lastContext.value) return

    const suggestion = suggestions.value.find(s => s.id === id)
    if (!suggestion) return

    try {
      const response = await apiClient.post('/api/v1/ai/generate', {
        ...lastContext.value,
        context: `Genera UNA alternativa diferente para: "${suggestion.text.substring(0, 50)}..."`,
        temperature: 0.9,
        mode: 'automatic'
      })

      if (response.data.success && response.data.suggestions.length > 0) {
        const newSuggestion = response.data.suggestions[0]
        newSuggestion.id = id  // Mantener el ID original

        const index = suggestions.value.findIndex(s => s.id === id)
        if (index !== -1) {
          suggestions.value[index] = newSuggestion
        }

        return newSuggestion
      }
    } catch (error) {
      console.error('[useAISuggestions] Error regenerando:', error)
      throw error
    }
  }

  return {
    // Estado
    suggestions,
    isGenerating,
    selectedSuggestion,
    config,
    hasSuggestions,

    // Acciones
    generate,
    selectSuggestion,
    updateSuggestion,
    clearSuggestions,
    regenerateSuggestion
  }
}
```

### 4.2 Composable useAIClients

```typescript
// frontend/src/composables/useAIClients.ts

import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

interface AIClient {
  id: string
  name: string
  context: string
  category: string
  active: boolean
  is_default: boolean
  settings?: Record<string, any>
  custom_prompts?: Record<string, string>
  created_at: string
  updated_at?: string
}

export function useAIClients() {
  const clients = ref<AIClient[]>([])
  const activeClientId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const activeClient = computed(() =>
    clients.value.find(c => c.id === activeClientId.value)
  )

  async function loadClients() {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/api/v1/settings/ai-clients')
      clients.value = response.data.clients
      activeClientId.value = response.data.active_client_id
    } catch (e: any) {
      error.value = e.message || 'Error cargando clientes'
      console.error('[useAIClients] Error:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function setActiveClient(clientId: string) {
    try {
      await apiClient.post(`/api/v1/settings/ai-clients/active/${clientId}`)
      activeClientId.value = clientId
      return true
    } catch (e: any) {
      error.value = e.message || 'Error estableciendo cliente activo'
      return false
    }
  }

  async function createClient(data: Partial<AIClient>) {
    try {
      const response = await apiClient.post('/api/v1/settings/ai-clients', data)
      clients.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Error creando cliente'
      throw e
    }
  }

  async function updateClient(clientId: string, data: Partial<AIClient>) {
    try {
      const response = await apiClient.patch(`/api/v1/settings/ai-clients/${clientId}`, data)
      const index = clients.value.findIndex(c => c.id === clientId)
      if (index !== -1) {
        clients.value[index] = response.data
      }
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Error actualizando cliente'
      throw e
    }
  }

  async function deleteClient(clientId: string) {
    try {
      await apiClient.delete(`/api/v1/settings/ai-clients/${clientId}`)
      clients.value = clients.value.filter(c => c.id !== clientId)
      return true
    } catch (e: any) {
      error.value = e.message || 'Error eliminando cliente'
      return false
    }
  }

  return {
    // Estado
    clients,
    activeClientId,
    activeClient,
    isLoading,
    error,

    // Acciones
    loadClients,
    setActiveClient,
    createClient,
    updateClient,
    deleteClient
  }
}
```

---

## 5. Migraci贸n de Base de Datos

```python
# backend/alembic/versions/xxx_add_ai_clients_table.py

"""Add AI clients table

Revision ID: xxx
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'ai_clients',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), default='general'),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('custom_prompts', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Insertar cliente por defecto
    op.execute("""
        INSERT INTO ai_clients (id, name, context, category, active, is_default)
        VALUES (
            'default',
            'Cliente Gen茅rico',
            'Eres un experto en crear anuncios comerciales efectivos y atractivos para negocios locales.',
            'general',
            true,
            true
        )
    """)

def downgrade():
    op.drop_table('ai_clients')
```

---

## 6. Integraci贸n con Rutas

```python
# backend/app/api/v1/api.py (actualizar)

from fastapi import APIRouter
from app.api.v1.endpoints import ai, audio, library, schedules, categories
from app.api.v1.endpoints.settings import voices, music, categories as settings_categories, automatic

# Importar nuevo router de clientes IA
from app.api.v1.endpoints.settings import ai_clients

api_router = APIRouter()

# ... routers existentes ...

# Agregar router de clientes IA en settings
api_router.include_router(
    ai_clients.router,
    prefix="/settings/ai-clients",
    tags=["AI Clients"]
)
```

---

## 7. Resumen de Archivos a Crear/Modificar

### Nuevos Archivos

| Archivo | Descripci贸n |
|---------|-------------|
| `backend/app/models/ai_client.py` | Modelo SQLAlchemy |
| `backend/app/schemas/ai_client.py` | Schemas Pydantic |
| `backend/app/services/ai/client_manager.py` | Servicio de gesti贸n |
| `backend/app/api/v1/endpoints/settings/ai_clients.py` | Endpoints API |
| `frontend/src/composables/useAISuggestions.ts` | Composable sugerencias |
| `frontend/src/composables/useAIClients.ts` | Composable clientes |
| `frontend/src/components/settings/ai/AIClientManager.vue` | UI gesti贸n clientes |
| `frontend/src/components/dashboard/AISuggestions.vue` | Componente dashboard |

### Archivos a Modificar

| Archivo | Cambios |
|---------|---------|
| `backend/app/services/ai/claude.py` | Agregar m茅todos con contexto |
| `backend/app/api/v1/endpoints/ai.py` | Nuevo endpoint generate |
| `backend/app/api/v1/api.py` | Incluir router ai_clients |

---

## 8. Flujo de Uso

```
1. Admin configura clientes en Settings > AI Clients
   鈹斺攢> Crea cliente con nombre y contexto de IA
   鈹斺攢> Establece uno como "activo"

2. Usuario en Dashboard genera sugerencias
   鈹斺攢> Escribe contexto del anuncio
   鈹斺攢> Selecciona tono y duraci贸n
   鈹斺攢> Click "Generar"

3. Backend procesa
   鈹斺攢> Obtiene contexto del cliente activo
   鈹斺攢> Construye prompt con contexto + tono + categor铆a
   鈹斺攢> Llama API Claude
   鈹斺攢> Parsea y retorna 2 sugerencias

4. Usuario selecciona sugerencia
   鈹斺攢> Click "Usar" env铆a texto al generador TTS
   鈹斺攢> Genera audio con la sugerencia seleccionada
```

---

## 9. Ejemplo de Contexto de Cliente

```json
{
  "id": "supermercado_lider",
  "name": "Supermercado L铆der",
  "context": "Eres un experto creando anuncios para Supermercado L铆der, la cadena l铆der de supermercados en Chile. Target: Familias chilenas, especialmente due帽as de casa. Propuesta de valor: 'Precios Bajos Todos los D铆as'. Tono: Cercano, confiable, ahorrativo, familiar. Beneficio estrella con Tarjeta L铆der BCI: 6% de devoluci贸n en compras.",
  "category": "supermercado",
  "active": true,
  "is_default": true,
  "custom_prompts": {
    "ofertas": "Enf贸cate en el ahorro y los precios bajos. Menciona 'Precios Bajos Todos los D铆as'.",
    "informacion": "Usa 'Estimados clientes' para mensajes operacionales."
  }
}
```

---

**Versi贸n**: 1.0
**Fecha**: 2024-12-09
**Autor**: Documentaci贸n generada por an谩lisis del sistema legacy

---

## 10. Estado de Implementacion

### Completado (100%)

| Componente | Archivo | Estado |
|------------|---------|--------|
| **Backend** | | |
| Modelo AIClient | `backend/app/models/ai_client.py` | Done |
| Schemas Pydantic | `backend/app/schemas/ai_client.py` | Done |
| Client Manager Service | `backend/app/services/ai/client_manager.py` | Done |
| Endpoints AI Clients | `backend/app/api/v1/endpoints/settings/ai_clients.py` | Done |
| Serializer | `backend/app/api/v1/serializers/ai_client_serializer.py` | Done |
| Claude Service mejorado | `backend/app/services/ai/claude.py` | Done |
| AI Endpoint `/generate` | `backend/app/api/v1/endpoints/ai.py` | Done |
| Migracion Alembic | `backend/alembic/versions/a1b2c3d4e5f6_add_ai_clients_table.py` | Done |
| **Frontend** | | |
| useAIClients composable | `frontend/src/composables/useAIClients.ts` | Done |
| useAISuggestions composable | `frontend/src/composables/useAISuggestions.ts` | Done |
| AIClientManager.vue | `frontend/src/components/settings/ai-clients/AIClientManager.vue` | Done |
| AIClientList.vue | `frontend/src/components/settings/ai-clients/components/AIClientList.vue` | Done |
| AIClientEditor.vue | `frontend/src/components/settings/ai-clients/components/AIClientEditor.vue` | Done |
| AIClientAddModal.vue | `frontend/src/components/settings/ai-clients/components/AIClientAddModal.vue` | Done |
| AIClientCard.vue | `frontend/src/components/settings/ai-clients/components/AIClientCard.vue` | Done |
| useAIClientManager.ts | `frontend/src/components/settings/ai-clients/composables/useAIClientManager.ts` | Done |
| AISuggestions.vue (Dashboard) | `frontend/src/components/dashboard/AISuggestions.vue` | Done |
| Router configurado | `frontend/src/router/index.ts` | Done |
| Tipos TypeScript | `frontend/src/types/audio.ts` | Done |
| API Client methods | `frontend/src/api/audio.ts` | Done |

### Rutas Disponibles

- `/settings/ai` - AI Clients Manager (gestion de clientes y contextos)
- `/dashboard` - Dashboard con AISuggestions integrado

---

**Version**: 2.0
**Fecha**: 2025-12-09
