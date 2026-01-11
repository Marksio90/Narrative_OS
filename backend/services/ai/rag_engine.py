"""
RAG (Retrieval Augmented Generation) Engine
Advanced canon-aware context retrieval using vector embeddings
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
import openai

from core.models.canon import Character, Location, Thread, Promise


@dataclass
class CanonFact:
    """A piece of canon knowledge"""
    entity_type: str  # 'character', 'location', 'thread', 'promise'
    entity_id: int
    name: str
    summary: str  # Concise description
    details: Dict[str, Any]  # Full data
    relevance_score: float  # 0-1, how relevant to current query
    embedding: Optional[np.ndarray] = None


class RAGEngine:
    """
    Retrieval Augmented Generation Engine

    Uses semantic search to find relevant canon facts:
    1. Embed all canon entities (characters, locations, etc.)
    2. Embed the current scene description
    3. Find most similar canon facts using cosine similarity
    4. Inject top-k facts into generation context
    """

    def __init__(
        self,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small"
    ):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model
        self.embedding_cache: Dict[str, np.ndarray] = {}

    async def retrieve_relevant_canon(
        self,
        query: str,
        project_id: int,
        db: Session,
        top_k: int = 10,
        entity_types: Optional[List[str]] = None,
        filter_ids: Optional[Dict[str, List[int]]] = None
    ) -> List[CanonFact]:
        """
        Retrieve most relevant canon facts for a query

        Args:
            query: Scene description or writing prompt
            project_id: Project ID to scope search
            db: Database session
            top_k: Number of facts to return
            entity_types: Filter by entity type (default: all)
            filter_ids: Filter by specific entity IDs (e.g., {'character_ids': [1, 3], 'location_ids': [2]})

        Returns:
            List of CanonFact objects ranked by relevance
        """
        # Get query embedding
        query_embedding = await self._get_embedding(query)

        # Load all canon entities
        canon_facts = await self._load_canon_entities(
            project_id,
            db,
            entity_types,
            filter_ids
        )

        # Compute relevance scores
        scored_facts = []
        for fact in canon_facts:
            if fact.embedding is not None:
                similarity = self._cosine_similarity(
                    query_embedding,
                    fact.embedding
                )
                fact.relevance_score = similarity
                scored_facts.append(fact)

        # Sort by relevance and return top k
        scored_facts.sort(key=lambda f: f.relevance_score, reverse=True)
        return scored_facts[:top_k]

    async def _load_canon_entities(
        self,
        project_id: int,
        db: Session,
        entity_types: Optional[List[str]],
        filter_ids: Optional[Dict[str, List[int]]] = None
    ) -> List[CanonFact]:
        """Load and embed all canon entities for a project"""
        facts = []

        # Characters
        if not entity_types or 'character' in entity_types:
            # Build query with optional ID filtering
            query_conditions = [
                Character.project_id == project_id,
                Character.deleted_at.is_(None)
            ]

            # Apply ID filter if provided
            if filter_ids and filter_ids.get('character_ids'):
                query_conditions.append(Character.id.in_(filter_ids['character_ids']))

            characters = db.execute(
                select(Character).where(and_(*query_conditions))
            ).scalars().all()

            for char in characters:
                summary = self._build_character_summary(char)
                embedding = await self._get_embedding(summary)

                facts.append(CanonFact(
                    entity_type='character',
                    entity_id=char.id,
                    name=char.name,
                    summary=summary,
                    details={
                        'role': char.role,
                        'personality': char.psychological_profile.get('personality', {}),
                        'goals': char.psychological_profile.get('core_desires', []),
                        'fears': char.psychological_profile.get('fears', []),
                        'voice': char.voice_profile
                    },
                    relevance_score=0.0,
                    embedding=embedding
                ))

        # Locations
        if not entity_types or 'location' in entity_types:
            # Build query with optional ID filtering
            query_conditions = [
                Location.project_id == project_id,
                Location.deleted_at.is_(None)
            ]

            # Apply ID filter if provided
            if filter_ids and filter_ids.get('location_ids'):
                query_conditions.append(Location.id.in_(filter_ids['location_ids']))

            locations = db.execute(
                select(Location).where(and_(*query_conditions))
            ).scalars().all()

            for loc in locations:
                summary = self._build_location_summary(loc)
                embedding = await self._get_embedding(summary)

                facts.append(CanonFact(
                    entity_type='location',
                    entity_id=loc.id,
                    name=loc.name,
                    summary=summary,
                    details={
                        'type': loc.type,
                        'description': loc.description,
                        'atmosphere': loc.physical_details.get('atmosphere', ''),
                        'significance': loc.story_significance
                    },
                    relevance_score=0.0,
                    embedding=embedding
                ))

        # Threads (plot threads)
        if not entity_types or 'thread' in entity_types:
            # Build query with optional ID filtering
            query_conditions = [
                Thread.project_id == project_id,
                Thread.deleted_at.is_(None)
            ]

            # Apply ID filter if provided
            if filter_ids and filter_ids.get('thread_ids'):
                query_conditions.append(Thread.id.in_(filter_ids['thread_ids']))

            threads = db.execute(
                select(Thread).where(and_(*query_conditions))
            ).scalars().all()

            for thread in threads:
                summary = self._build_thread_summary(thread)
                embedding = await self._get_embedding(summary)

                facts.append(CanonFact(
                    entity_type='thread',
                    entity_id=thread.id,
                    name=thread.title,
                    summary=summary,
                    details={
                        'type': thread.thread_type,
                        'status': thread.status,
                        'description': thread.description
                    },
                    relevance_score=0.0,
                    embedding=embedding
                ))

        # Promises (setup/payoff tracking)
        if not entity_types or 'promise' in entity_types:
            promises = db.execute(
                select(Promise).where(
                    and_(
                        Promise.project_id == project_id,
                        Promise.deleted_at.is_(None)
                    )
                )
            ).scalars().all()

            for promise in promises:
                summary = self._build_promise_summary(promise)
                embedding = await self._get_embedding(summary)

                facts.append(CanonFact(
                    entity_type='promise',
                    entity_id=promise.id,
                    name=promise.promise_text[:50] + "...",
                    summary=summary,
                    details={
                        'promise_text': promise.promise_text,
                        'type': promise.promise_type,
                        'payoff_text': promise.payoff_text,
                        'status': promise.status
                    },
                    relevance_score=0.0,
                    embedding=embedding
                ))

        return facts

    def _build_character_summary(self, char: Character) -> str:
        """Build searchable text summary of a character"""
        parts = [
            f"{char.name} is a {char.role}.",
            char.description or "",
        ]

        # Add personality
        psych = char.psychological_profile or {}
        if 'personality' in psych:
            parts.append(f"Personality: {psych['personality']}")

        # Add core desires
        if 'core_desires' in psych:
            desires = ', '.join(psych['core_desires'][:3])
            parts.append(f"Wants: {desires}")

        # Add voice notes
        if char.voice_profile:
            parts.append(f"Voice: {char.voice_profile.get('summary', '')}")

        return " ".join(filter(None, parts))

    def _build_location_summary(self, loc: Location) -> str:
        """Build searchable text summary of a location"""
        parts = [
            f"{loc.name} is a {loc.type}.",
            loc.description or "",
        ]

        # Add physical details
        if loc.physical_details:
            atmos = loc.physical_details.get('atmosphere', '')
            if atmos:
                parts.append(f"Atmosphere: {atmos}")

        # Add significance
        if loc.story_significance:
            parts.append(f"Significance: {loc.story_significance}")

        return " ".join(filter(None, parts))

    def _build_thread_summary(self, thread: Thread) -> str:
        """Build searchable text summary of a plot thread"""
        parts = [
            f"{thread.title} ({thread.thread_type})",
            thread.description or "",
        ]
        return " ".join(filter(None, parts))

    def _build_promise_summary(self, promise: Promise) -> str:
        """Build searchable text summary of a promise"""
        parts = [
            f"Promise: {promise.promise_text}",
        ]
        if promise.payoff_text:
            parts.append(f"Payoff: {promise.payoff_text}")

        return " ".join(filter(None, parts))

    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text (with caching)"""
        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        # Call OpenAI embeddings API
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )

        embedding = np.array(response.data[0].embedding)

        # Cache for reuse
        self.embedding_cache[text] = embedding

        return embedding

    def _cosine_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    async def build_context_summary(
        self,
        canon_facts: List[CanonFact],
        max_length: int = 2000
    ) -> str:
        """
        Build a concise context summary from canon facts

        Args:
            canon_facts: Relevant canon facts
            max_length: Maximum character length

        Returns:
            Formatted context string
        """
        # Group by entity type
        by_type: Dict[str, List[CanonFact]] = {}
        for fact in canon_facts:
            if fact.entity_type not in by_type:
                by_type[fact.entity_type] = []
            by_type[fact.entity_type].append(fact)

        # Build summary sections
        sections = []

        if 'character' in by_type:
            chars = by_type['character']
            section = "CHARACTERS:\n"
            for char in chars[:5]:  # Top 5 most relevant
                section += f"• {char.name}: {char.summary}\n"
            sections.append(section)

        if 'location' in by_type:
            locs = by_type['location']
            section = "LOCATIONS:\n"
            for loc in locs[:3]:
                section += f"• {loc.name}: {loc.summary}\n"
            sections.append(section)

        if 'thread' in by_type:
            threads = by_type['thread']
            section = "PLOT THREADS:\n"
            for thread in threads[:3]:
                section += f"• {thread.name}: {thread.summary}\n"
            sections.append(section)

        if 'promise' in by_type:
            promises = by_type['promise']
            section = "PROMISES:\n"
            for p in promises[:3]:
                status = p.details.get('status', 'pending')
                section += f"• {p.summary} [Status: {status}]\n"
            sections.append(section)

        full_summary = "\n".join(sections)

        # Truncate if too long
        if len(full_summary) > max_length:
            full_summary = full_summary[:max_length] + "..."

        return full_summary
