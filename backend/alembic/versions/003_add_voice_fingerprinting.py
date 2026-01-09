"""Add voice fingerprinting tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-09

Character Voice Fingerprinting feature:
- character_voice_fingerprints: Linguistic profiles for dialogue consistency
- dialogue_lines: Extracted dialogue with attribution
- dialogue_consistency_scores: Consistency tracking per scene
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === Create character_voice_fingerprints table ===
    op.create_table(
        'character_voice_fingerprints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),

        # Vocabulary Analysis
        sa.Column('vocabulary_profile', postgresql.JSONB, nullable=False, comment="""
            {
                'word_frequency': {word: count},
                'avg_word_length': float,
                'unique_word_ratio': float,
                'rarity_score': float,  # 0-1, how rare words are
                'top_words': [word1, word2, ...],
                'avoided_words': [word1, word2, ...]
            }
        """),

        # Syntax Analysis
        sa.Column('syntax_profile', postgresql.JSONB, nullable=False, comment="""
            {
                'avg_sentence_length': float,
                'sentence_length_variance': float,
                'complexity_score': float,  # 0-1
                'question_frequency': float,
                'exclamation_frequency': float,
                'subordinate_clause_frequency': float
            }
        """),

        # Linguistic Markers
        sa.Column('linguistic_markers', postgresql.JSONB, nullable=False, comment="""
            {
                'catchphrases': [str],
                'filler_words': [str],
                'sentence_starters': [str],
                'quirks': [str],
                'contractions_ratio': float,
                'profanity_frequency': float
            }
        """),

        # Emotional Baseline
        sa.Column('emotional_baseline', postgresql.JSONB, nullable=False, comment="""
            {
                'joy': float,
                'anger': float,
                'sadness': float,
                'fear': float,
                'surprise': float,
                'neutral': float,
                'dominant_emotion': str
            }
        """),

        # Formality & Style
        sa.Column('formality_score', sa.Float(), nullable=False, comment="0-1, casual to formal"),
        sa.Column('confidence_score', sa.Float(), nullable=False, comment="0-1, how confident the fingerprint is"),

        # Metadata
        sa.Column('sample_count', sa.Integer(), nullable=False, comment="Number of dialogue samples analyzed"),
        sa.Column('total_words', sa.Integer(), nullable=False, comment="Total words analyzed"),
        sa.Column('last_analyzed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('character_id', name='uq_voice_fingerprint_character')
    )

    # Indexes for character_voice_fingerprints
    op.create_index('ix_voice_fingerprints_character_id', 'character_voice_fingerprints', ['character_id'])
    op.create_index('ix_voice_fingerprints_last_analyzed', 'character_voice_fingerprints', ['last_analyzed_at'])

    # === Create dialogue_lines table ===
    op.create_table(
        'dialogue_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True, comment="Scene this dialogue is from"),
        sa.Column('character_id', sa.Integer(), nullable=False, comment="Who spoke this line"),

        # Content
        sa.Column('text', sa.Text(), nullable=False, comment="The dialogue text (without quotes)"),
        sa.Column('context', sa.Text(), nullable=True, comment="Surrounding prose for context"),

        # Metadata
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('extracted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE')
    )

    # Indexes for dialogue_lines
    op.create_index('ix_dialogue_lines_project_id', 'dialogue_lines', ['project_id'])
    op.create_index('ix_dialogue_lines_character_id', 'dialogue_lines', ['character_id'])
    op.create_index('ix_dialogue_lines_scene_id', 'dialogue_lines', ['scene_id'])
    op.create_index('ix_dialogue_lines_extracted_at', 'dialogue_lines', ['extracted_at'])

    # === Create dialogue_consistency_scores table ===
    op.create_table(
        'dialogue_consistency_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True, comment="Scene being checked"),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('fingerprint_id', sa.Integer(), nullable=False),

        # Scores
        sa.Column('overall_score', sa.Float(), nullable=False, comment="0-1, overall consistency"),
        sa.Column('vocabulary_score', sa.Float(), nullable=False, comment="0-1, word choice consistency"),
        sa.Column('syntax_score', sa.Float(), nullable=False, comment="0-1, sentence structure consistency"),
        sa.Column('formality_score', sa.Float(), nullable=False, comment="0-1, formality match"),
        sa.Column('emotional_score', sa.Float(), nullable=False, comment="0-1, emotional tone match"),

        # Issues & Suggestions
        sa.Column('issues', postgresql.JSONB, nullable=False, comment="""
            [
                {
                    'type': 'vocabulary'|'syntax'|'formality'|'emotion',
                    'severity': 'low'|'medium'|'high',
                    'description': str,
                    'line_number': int,
                    'problematic_text': str
                }
            ]
        """),
        sa.Column('suggestions', postgresql.JSONB, nullable=False, comment="""
            [
                {
                    'issue_index': int,
                    'original_text': str,
                    'suggested_text': str,
                    'reason': str
                }
            ]
        """),

        # Metadata
        sa.Column('dialogue_text', sa.Text(), nullable=False, comment="The dialogue that was checked"),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fingerprint_id'], ['character_voice_fingerprints.id'], ondelete='CASCADE')
    )

    # Indexes for dialogue_consistency_scores
    op.create_index('ix_consistency_scores_scene_id', 'dialogue_consistency_scores', ['scene_id'])
    op.create_index('ix_consistency_scores_character_id', 'dialogue_consistency_scores', ['character_id'])
    op.create_index('ix_consistency_scores_fingerprint_id', 'dialogue_consistency_scores', ['fingerprint_id'])
    op.create_index('ix_consistency_scores_created_at', 'dialogue_consistency_scores', ['created_at'])
    op.create_index('ix_consistency_scores_overall_score', 'dialogue_consistency_scores', ['overall_score'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('dialogue_consistency_scores')
    op.drop_table('dialogue_lines')
    op.drop_table('character_voice_fingerprints')
