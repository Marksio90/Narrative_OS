"""
Character Voice Fingerprinting Service

Analyzes dialogue patterns to create unique linguistic fingerprints
Ensures character voice consistency across 100k+ word novels
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import statistics
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from core.models.canon import (
    Character,
    CharacterVoiceFingerprint,
    DialogueLine,
    DialogueConsistencyScore
)


@dataclass
class VocabularyProfile:
    """Vocabulary analysis results"""
    word_frequency: Dict[str, int]
    avg_word_length: float
    unique_word_ratio: float
    rarity_score: float
    top_words: List[str]
    avoided_words: List[str]


@dataclass
class SyntaxProfile:
    """Syntax analysis results"""
    avg_sentence_length: float
    sentence_length_variance: float
    complexity_score: float
    question_frequency: float
    exclamation_frequency: float
    subordinate_clause_frequency: float


@dataclass
class LinguisticMarkers:
    """Linguistic quirks and patterns"""
    catchphrases: List[str]
    filler_words: List[str]
    sentence_starters: List[str]
    quirks: List[str]
    contractions_ratio: float
    profanity_frequency: float


@dataclass
class EmotionalBaseline:
    """Emotional tone distribution"""
    joy: float
    anger: float
    sadness: float
    fear: float
    surprise: float
    neutral: float
    dominant_emotion: str


@dataclass
class ConsistencyIssue:
    """A detected consistency issue"""
    type: str  # vocabulary, syntax, formality, emotion
    severity: str  # low, medium, high
    description: str
    line_number: int
    problematic_text: str


@dataclass
class ConsistencySuggestion:
    """Suggested fix for an issue"""
    issue_index: int
    original_text: str
    suggested_text: str
    reason: str


@dataclass
class ConsistencyResult:
    """Complete consistency check result"""
    overall_score: float
    vocabulary_score: float
    syntax_score: float
    formality_score: float
    emotional_score: float
    issues: List[ConsistencyIssue]
    suggestions: List[ConsistencySuggestion]


class VoiceFingerprintService:
    """
    Service for analyzing and scoring character voice consistency

    Features:
    - Dialogue extraction from prose
    - Linguistic pattern analysis
    - Voice fingerprint creation
    - Consistency scoring
    - Improvement suggestions
    """

    def __init__(self, db: Session):
        self.db = db

    # === Dialogue Extraction ===

    def extract_dialogue_from_prose(
        self,
        prose: str,
        character_name: str,
        context_window: int = 100
    ) -> List[Tuple[str, str]]:
        """
        Extract dialogue lines for a specific character

        Args:
            prose: Full prose text
            character_name: Name of character to extract dialogue for
            context_window: Characters of context to include around dialogue

        Returns:
            List of (dialogue_text, context) tuples
        """
        dialogue_lines = []

        # Regex patterns for dialogue
        # Matches: "dialogue" or 'dialogue' or "dialogue," or 'dialogue.'
        dialogue_pattern = r'["\']([^"\']+)["\']'

        # Find all dialogue with context
        for match in re.finditer(dialogue_pattern, prose):
            dialogue_text = match.group(1)
            start_pos = match.start()
            end_pos = match.end()

            # Get surrounding context
            context_start = max(0, start_pos - context_window)
            context_end = min(len(prose), end_pos + context_window)
            context = prose[context_start:context_end]

            # Check if character name appears in context
            # This is a simple attribution - can be improved with AI
            if character_name.lower() in context.lower():
                dialogue_lines.append((dialogue_text, context))

        return dialogue_lines

    async def extract_and_store_dialogue(
        self,
        project_id: int,
        scene_id: Optional[int],
        prose: str,
        character_id: int,
        character_name: str
    ) -> int:
        """
        Extract dialogue and store in database

        Returns:
            Number of dialogue lines extracted
        """
        dialogue_tuples = self.extract_dialogue_from_prose(prose, character_name)

        count = 0
        for dialogue_text, context in dialogue_tuples:
            word_count = len(dialogue_text.split())

            dialogue_line = DialogueLine(
                project_id=project_id,
                scene_id=scene_id,
                character_id=character_id,
                text=dialogue_text,
                context=context,
                word_count=word_count,
                extracted_at=datetime.utcnow()
            )

            self.db.add(dialogue_line)
            count += 1

        if count > 0:
            self.db.commit()

        return count

    # === Linguistic Analysis ===

    def analyze_vocabulary(self, dialogue_samples: List[str]) -> VocabularyProfile:
        """
        Analyze vocabulary patterns

        Args:
            dialogue_samples: List of dialogue strings

        Returns:
            VocabularyProfile with analysis results
        """
        # Combine all dialogue
        all_text = " ".join(dialogue_samples)
        words = re.findall(r'\b\w+\b', all_text.lower())

        if not words:
            return VocabularyProfile(
                word_frequency={},
                avg_word_length=0.0,
                unique_word_ratio=0.0,
                rarity_score=0.0,
                top_words=[],
                avoided_words=[]
            )

        # Word frequency
        word_freq = Counter(words)

        # Average word length
        avg_word_length = statistics.mean(len(word) for word in words)

        # Unique word ratio
        unique_word_ratio = len(set(words)) / len(words) if words else 0.0

        # Rarity score (based on word length as proxy)
        # Real implementation would use word frequency corpus
        rarity_score = min(1.0, avg_word_length / 10.0)

        # Top words (excluding common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'i', 'you', 'to', 'of', 'in', 'on', 'at', 'for'}
        top_words = [
            word for word, count in word_freq.most_common(20)
            if word not in common_words
        ][:10]

        return VocabularyProfile(
            word_frequency=dict(word_freq.most_common(50)),
            avg_word_length=avg_word_length,
            unique_word_ratio=unique_word_ratio,
            rarity_score=rarity_score,
            top_words=top_words,
            avoided_words=[]  # Would need corpus comparison
        )

    def analyze_syntax(self, dialogue_samples: List[str]) -> SyntaxProfile:
        """
        Analyze sentence structure patterns

        Args:
            dialogue_samples: List of dialogue strings

        Returns:
            SyntaxProfile with analysis results
        """
        sentence_lengths = []
        question_count = 0
        exclamation_count = 0
        subordinate_count = 0
        total_sentences = 0

        for dialogue in dialogue_samples:
            # Split into sentences
            sentences = re.split(r'[.!?]+', dialogue)
            sentences = [s.strip() for s in sentences if s.strip()]

            for sentence in sentences:
                total_sentences += 1

                # Sentence length
                words = len(sentence.split())
                sentence_lengths.append(words)

                # Question detection
                if '?' in sentence:
                    question_count += 1

                # Exclamation detection
                if '!' in sentence:
                    exclamation_count += 1

                # Subordinate clauses (rough detection)
                subordinate_markers = ['because', 'although', 'while', 'since', 'if', 'when', 'that', 'which']
                if any(marker in sentence.lower() for marker in subordinate_markers):
                    subordinate_count += 1

        if not sentence_lengths:
            return SyntaxProfile(
                avg_sentence_length=0.0,
                sentence_length_variance=0.0,
                complexity_score=0.0,
                question_frequency=0.0,
                exclamation_frequency=0.0,
                subordinate_clause_frequency=0.0
            )

        avg_sentence_length = statistics.mean(sentence_lengths)
        sentence_variance = statistics.variance(sentence_lengths) if len(sentence_lengths) > 1 else 0.0

        # Complexity score based on sentence length and subordinate clauses
        complexity_score = min(1.0, (avg_sentence_length / 20.0 + subordinate_count / total_sentences) / 2)

        return SyntaxProfile(
            avg_sentence_length=avg_sentence_length,
            sentence_length_variance=sentence_variance,
            complexity_score=complexity_score,
            question_frequency=question_count / total_sentences if total_sentences > 0 else 0.0,
            exclamation_frequency=exclamation_count / total_sentences if total_sentences > 0 else 0.0,
            subordinate_clause_frequency=subordinate_count / total_sentences if total_sentences > 0 else 0.0
        )

    def detect_linguistic_markers(self, dialogue_samples: List[str]) -> LinguisticMarkers:
        """
        Detect linguistic quirks and patterns

        Args:
            dialogue_samples: List of dialogue strings

        Returns:
            LinguisticMarkers with detected patterns
        """
        all_text = " ".join(dialogue_samples)

        # Common filler words
        filler_words_pattern = r'\b(um|uh|like|you know|well|so|actually|basically|literally)\b'
        filler_matches = re.findall(filler_words_pattern, all_text.lower())
        filler_words = list(set(filler_matches))

        # Sentence starters
        sentences = re.split(r'[.!?]+', all_text)
        sentence_starters = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                first_words = ' '.join(sentence.split()[:2]).lower()
                sentence_starters.append(first_words)

        # Get most common starters
        starter_freq = Counter(sentence_starters)
        common_starters = [starter for starter, count in starter_freq.most_common(5) if count > 2]

        # Contractions ratio
        contractions_pattern = r"\b\w+'\w+\b"
        contractions_count = len(re.findall(contractions_pattern, all_text))
        total_words = len(all_text.split())
        contractions_ratio = contractions_count / total_words if total_words > 0 else 0.0

        # Detect repeated phrases (potential catchphrases)
        # Look for 2-4 word phrases that repeat
        catchphrases = []
        for n in [2, 3, 4]:
            words = all_text.lower().split()
            ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
            ngram_freq = Counter(ngrams)
            for ngram, count in ngram_freq.items():
                if count >= 3:  # Appears at least 3 times
                    catchphrases.append(ngram)

        return LinguisticMarkers(
            catchphrases=catchphrases[:5],  # Top 5
            filler_words=filler_words,
            sentence_starters=common_starters,
            quirks=[],  # Would need more sophisticated NLP
            contractions_ratio=contractions_ratio,
            profanity_frequency=0.0  # Would need profanity dictionary
        )

    def estimate_formality(self, dialogue_samples: List[str]) -> float:
        """
        Estimate formality score (0=casual, 1=formal)

        Args:
            dialogue_samples: List of dialogue strings

        Returns:
            Formality score 0-1
        """
        all_text = " ".join(dialogue_samples)

        formality_indicators = {
            'formal': [
                'however', 'therefore', 'consequently', 'nevertheless',
                'furthermore', 'moreover', 'additionally', 'indeed',
                'certainly', 'undoubtedly', 'shall', 'ought'
            ],
            'casual': [
                'yeah', 'nah', 'gonna', 'wanna', 'gotta', 'kinda',
                'sorta', 'dunno', 'ain\'t', 'y\'know', 'hey', 'wow'
            ]
        }

        formal_count = sum(1 for word in formality_indicators['formal'] if word in all_text.lower())
        casual_count = sum(1 for word in formality_indicators['casual'] if word in all_text.lower())

        # Contractions suggest informality
        contractions_count = len(re.findall(r"\b\w+'\w+\b", all_text))

        # Calculate score
        total_indicators = formal_count + casual_count + contractions_count
        if total_indicators == 0:
            return 0.5  # Neutral

        formality_score = (formal_count - casual_count - contractions_count * 0.5) / total_indicators

        # Normalize to 0-1
        return max(0.0, min(1.0, (formality_score + 1.0) / 2.0))

    # === Voice Fingerprint Creation ===

    async def create_voice_fingerprint(
        self,
        character_id: int
    ) -> CharacterVoiceFingerprint:
        """
        Create or update voice fingerprint for a character

        Args:
            character_id: Character ID

        Returns:
            CharacterVoiceFingerprint object
        """
        # Load all dialogue for this character
        dialogue_lines = self.db.execute(
            select(DialogueLine).where(
                DialogueLine.character_id == character_id
            )
        ).scalars().all()

        if not dialogue_lines:
            raise ValueError(f"No dialogue found for character {character_id}")

        dialogue_samples = [line.text for line in dialogue_lines]

        # Run all analyses
        vocab_profile = self.analyze_vocabulary(dialogue_samples)
        syntax_profile = self.analyze_syntax(dialogue_samples)
        linguistic_markers = self.detect_linguistic_markers(dialogue_samples)
        formality_score = self.estimate_formality(dialogue_samples)

        # For emotional baseline, we'd use sentiment analysis (placeholder for now)
        emotional_baseline = EmotionalBaseline(
            joy=0.2,
            anger=0.1,
            sadness=0.1,
            fear=0.1,
            surprise=0.1,
            neutral=0.4,
            dominant_emotion="neutral"
        )

        # Calculate confidence score based on sample size
        sample_count = len(dialogue_samples)
        total_words = sum(line.word_count for line in dialogue_lines)
        confidence_score = min(1.0, sample_count / 50.0)  # Full confidence at 50+ samples

        # Check if fingerprint exists
        existing = self.db.execute(
            select(CharacterVoiceFingerprint).where(
                CharacterVoiceFingerprint.character_id == character_id
            )
        ).scalar_one_or_none()

        if existing:
            # Update existing
            existing.vocabulary_profile = {
                'word_frequency': vocab_profile.word_frequency,
                'avg_word_length': vocab_profile.avg_word_length,
                'unique_word_ratio': vocab_profile.unique_word_ratio,
                'rarity_score': vocab_profile.rarity_score,
                'top_words': vocab_profile.top_words,
                'avoided_words': vocab_profile.avoided_words
            }
            existing.syntax_profile = {
                'avg_sentence_length': syntax_profile.avg_sentence_length,
                'sentence_length_variance': syntax_profile.sentence_length_variance,
                'complexity_score': syntax_profile.complexity_score,
                'question_frequency': syntax_profile.question_frequency,
                'exclamation_frequency': syntax_profile.exclamation_frequency,
                'subordinate_clause_frequency': syntax_profile.subordinate_clause_frequency
            }
            existing.linguistic_markers = {
                'catchphrases': linguistic_markers.catchphrases,
                'filler_words': linguistic_markers.filler_words,
                'sentence_starters': linguistic_markers.sentence_starters,
                'quirks': linguistic_markers.quirks,
                'contractions_ratio': linguistic_markers.contractions_ratio,
                'profanity_frequency': linguistic_markers.profanity_frequency
            }
            existing.emotional_baseline = {
                'joy': emotional_baseline.joy,
                'anger': emotional_baseline.anger,
                'sadness': emotional_baseline.sadness,
                'fear': emotional_baseline.fear,
                'surprise': emotional_baseline.surprise,
                'neutral': emotional_baseline.neutral,
                'dominant_emotion': emotional_baseline.dominant_emotion
            }
            existing.formality_score = formality_score
            existing.confidence_score = confidence_score
            existing.sample_count = sample_count
            existing.total_words = total_words
            existing.last_analyzed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new
            fingerprint = CharacterVoiceFingerprint(
                character_id=character_id,
                vocabulary_profile={
                    'word_frequency': vocab_profile.word_frequency,
                    'avg_word_length': vocab_profile.avg_word_length,
                    'unique_word_ratio': vocab_profile.unique_word_ratio,
                    'rarity_score': vocab_profile.rarity_score,
                    'top_words': vocab_profile.top_words,
                    'avoided_words': vocab_profile.avoided_words
                },
                syntax_profile={
                    'avg_sentence_length': syntax_profile.avg_sentence_length,
                    'sentence_length_variance': syntax_profile.sentence_length_variance,
                    'complexity_score': syntax_profile.complexity_score,
                    'question_frequency': syntax_profile.question_frequency,
                    'exclamation_frequency': syntax_profile.exclamation_frequency,
                    'subordinate_clause_frequency': syntax_profile.subordinate_clause_frequency
                },
                linguistic_markers={
                    'catchphrases': linguistic_markers.catchphrases,
                    'filler_words': linguistic_markers.filler_words,
                    'sentence_starters': linguistic_markers.sentence_starters,
                    'quirks': linguistic_markers.quirks,
                    'contractions_ratio': linguistic_markers.contractions_ratio,
                    'profanity_frequency': linguistic_markers.profanity_frequency
                },
                emotional_baseline={
                    'joy': emotional_baseline.joy,
                    'anger': emotional_baseline.anger,
                    'sadness': emotional_baseline.sadness,
                    'fear': emotional_baseline.fear,
                    'surprise': emotional_baseline.surprise,
                    'neutral': emotional_baseline.neutral,
                    'dominant_emotion': emotional_baseline.dominant_emotion
                },
                formality_score=formality_score,
                confidence_score=confidence_score,
                sample_count=sample_count,
                total_words=total_words,
                last_analyzed_at=datetime.utcnow()
            )

            self.db.add(fingerprint)
            self.db.commit()
            self.db.refresh(fingerprint)
            return fingerprint

    # === Consistency Scoring ===

    async def check_dialogue_consistency(
        self,
        character_id: int,
        dialogue_text: str,
        scene_id: Optional[int] = None
    ) -> ConsistencyResult:
        """
        Check if dialogue is consistent with character's voice fingerprint

        Args:
            character_id: Character ID
            dialogue_text: New dialogue to check
            scene_id: Optional scene ID for tracking

        Returns:
            ConsistencyResult with scores and suggestions
        """
        # Load fingerprint
        fingerprint = self.db.execute(
            select(CharacterVoiceFingerprint).where(
                CharacterVoiceFingerprint.character_id == character_id
            )
        ).scalar_one_or_none()

        if not fingerprint:
            raise ValueError(f"No voice fingerprint found for character {character_id}")

        # Analyze new dialogue
        new_vocab = self.analyze_vocabulary([dialogue_text])
        new_syntax = self.analyze_syntax([dialogue_text])
        new_formality = self.estimate_formality([dialogue_text])

        # Compare with fingerprint
        issues = []
        suggestions = []

        # Vocabulary score
        baseline_avg_word_len = fingerprint.vocabulary_profile.get('avg_word_length', 5.0)
        vocab_diff = abs(new_vocab.avg_word_length - baseline_avg_word_len)
        vocab_score = max(0.0, 1.0 - (vocab_diff / 3.0))  # Penalize if >3 char difference

        if vocab_diff > 2.0:
            issues.append(ConsistencyIssue(
                type='vocabulary',
                severity='medium' if vocab_diff > 3.0 else 'low',
                description=f"Word length mismatch: {new_vocab.avg_word_length:.1f} vs baseline {baseline_avg_word_len:.1f}",
                line_number=0,
                problematic_text=dialogue_text[:100]
            ))

        # Syntax score
        baseline_sent_len = fingerprint.syntax_profile.get('avg_sentence_length', 10.0)
        syntax_diff = abs(new_syntax.avg_sentence_length - baseline_sent_len)
        syntax_score = max(0.0, 1.0 - (syntax_diff / 10.0))

        if syntax_diff > 5.0:
            issues.append(ConsistencyIssue(
                type='syntax',
                severity='medium' if syntax_diff > 8.0 else 'low',
                description=f"Sentence length mismatch: {new_syntax.avg_sentence_length:.1f} vs baseline {baseline_sent_len:.1f}",
                line_number=0,
                problematic_text=dialogue_text[:100]
            ))

        # Formality score
        baseline_formality = fingerprint.formality_score
        formality_diff = abs(new_formality - baseline_formality)
        formality_score = max(0.0, 1.0 - formality_diff)

        if formality_diff > 0.3:
            issues.append(ConsistencyIssue(
                type='formality',
                severity='high' if formality_diff > 0.5 else 'medium',
                description=f"Formality mismatch: {'too formal' if new_formality > baseline_formality else 'too casual'}",
                line_number=0,
                problematic_text=dialogue_text[:100]
            ))

        # Overall score (weighted average)
        overall_score = (vocab_score * 0.3 + syntax_score * 0.3 + formality_score * 0.4)

        # Store result in database
        consistency_record = DialogueConsistencyScore(
            scene_id=scene_id,
            character_id=character_id,
            fingerprint_id=fingerprint.id,
            overall_score=overall_score,
            vocabulary_score=vocab_score,
            syntax_score=syntax_score,
            formality_score=formality_score,
            emotional_score=0.5,  # Placeholder
            issues=[{
                'type': issue.type,
                'severity': issue.severity,
                'description': issue.description,
                'line_number': issue.line_number,
                'problematic_text': issue.problematic_text
            } for issue in issues],
            suggestions=[{
                'issue_index': sug.issue_index,
                'original_text': sug.original_text,
                'suggested_text': sug.suggested_text,
                'reason': sug.reason
            } for sug in suggestions],
            dialogue_text=dialogue_text
        )

        self.db.add(consistency_record)
        self.db.commit()

        return ConsistencyResult(
            overall_score=overall_score,
            vocabulary_score=vocab_score,
            syntax_score=syntax_score,
            formality_score=formality_score,
            emotional_score=0.5,
            issues=issues,
            suggestions=suggestions
        )
