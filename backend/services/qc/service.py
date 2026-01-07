"""
Quality Control Service

Multi-agent writers' room validation system

Validates:
- Continuity (timeline, locations, items)
- Character consistency (behavior, voice)
- Plot logic (setups, payoffs, causality)
- Canon Contracts compliance
- Promise/Payoff status
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.llm import get_llm, LLMMessage, LLMConfig
from services.canon.contracts import CanonContractsService
from services.canon.promise_ledger import PromiseLedgerService


class QCIssue:
    """
    Quality control issue found during validation
    """
    def __init__(
        self,
        category: str,  # continuity, character, plot, contract, style
        severity: str,  # blocker, warning, suggestion
        description: str,
        location: Optional[str] = None,  # Where in text
        suggested_fix: Optional[str] = None,
    ):
        self.category = category
        self.severity = severity
        self.description = description
        self.location = location
        self.suggested_fix = suggested_fix

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "location": self.location,
            "suggested_fix": self.suggested_fix,
        }


class QCService:
    """
    Quality Control Service

    Implements "writers' room" multi-agent validation
    """

    def __init__(self, db: Session):
        self.db = db
        self.contracts_service = CanonContractsService(db)
        self.promise_service = PromiseLedgerService(db)

    # ===== Full Chapter QC =====

    async def validate_chapter(
        self,
        project_id: int,
        chapter_content: str,
        chapter_metadata: Dict[str, Any],
        canon_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run complete QC validation on chapter

        Args:
            project_id: Project ID
            chapter_content: Full chapter text
            chapter_metadata: Chapter info (number, POV, etc.)
            canon_context: Relevant canon (characters, locations, rules)

        Returns:
            Comprehensive QC report
        """
        issues = []

        # Run all validation agents in parallel (conceptually)
        # In practice, we'll run them sequentially for simplicity

        # 1. Continuity Check
        continuity_issues = await self._check_continuity(
            chapter_content,
            chapter_metadata,
            canon_context,
        )
        issues.extend(continuity_issues)

        # 2. Character Consistency
        character_issues = await self._check_character_consistency(
            chapter_content,
            chapter_metadata,
            canon_context,
        )
        issues.extend(character_issues)

        # 3. Plot Logic
        plot_issues = await self._check_plot_logic(
            chapter_content,
            chapter_metadata,
            canon_context,
        )
        issues.extend(plot_issues)

        # 4. Canon Contracts
        contract_violations = await self.contracts_service.validate_text(
            project_id=project_id,
            text=chapter_content,
            context=chapter_metadata,
        )
        issues.extend([
            QCIssue(
                category="contract",
                severity="blocker" if v.severity == "must" else "warning",
                description=v.violation_description,
                suggested_fix=v.suggested_fix,
            )
            for v in contract_violations
        ])

        # 5. Promise Detection (for new promises)
        detected_promises = await self.promise_service.detect_promises(
            text=chapter_content,
            chapter=chapter_metadata.get("chapter_number", 1),
            context=chapter_metadata,
        )

        # Calculate overall score
        score = self._calculate_qc_score(issues)

        # Determine if chapter passes
        blockers = [i for i in issues if i.severity == "blocker"]
        passed = len(blockers) == 0

        return {
            "passed": passed,
            "score": score,
            "issues": [i.to_dict() for i in issues],
            "issue_count": len(issues),
            "blockers": len(blockers),
            "warnings": len([i for i in issues if i.severity == "warning"]),
            "suggestions": len([i for i in issues if i.severity == "suggestion"]),
            "detected_promises": [p.to_dict() for p in detected_promises],
            "breakdown": self._categorize_issues(issues),
        }

    # ===== Individual Validation Agents =====

    async def _check_continuity(
        self,
        text: str,
        metadata: Dict[str, Any],
        canon: Dict[str, Any],
    ) -> List[QCIssue]:
        """
        Continuity Editor Agent

        Checks:
        - Timeline consistency
        - Location logic (can characters get there?)
        - Item tracking (who has what?)
        - Physical impossibilities
        """
        prompt = self._build_continuity_prompt(canon)
        messages = [
            LLMMessage(role="system", content=prompt),
            LLMMessage(
                role="user",
                content=self._build_continuity_request(text, metadata, canon),
            ),
        ]

        llm = get_llm()
        config = LLMConfig(model="gpt-4", temperature=0.2, max_tokens=1000)

        try:
            response = await llm.complete(messages, config)
            issues = self._parse_qc_response(response.content, "continuity")
            return issues
        except Exception as e:
            print(f"Continuity check error: {e}")
            return []

    def _build_continuity_prompt(self, canon: Dict[str, Any]) -> str:
        """Build prompt for continuity agent"""
        return """You are the Continuity Editor in a writers' room.

Your job is to catch continuity errors:

**Timeline errors:**
- Events happening in wrong order
- Time passing inconsistently
- Dates/seasons that don't match

**Location errors:**
- Characters teleporting
- Impossible travel times
- Wrong locations for scenes

**Item tracking:**
- Objects appearing/disappearing
- Wrong owners
- Physical impossibilities

**Physical logic:**
- Characters doing impossible things
- Wounds healing instantly
- Contradictions with established facts

**Output format:**

ISSUE:
SEVERITY: blocker/warning/suggestion
DESCRIPTION: [what's wrong]
LOCATION: [where in text]
FIX: [how to fix]
---

Be thorough - even small continuity breaks ruin reader immersion.
"""

    def _build_continuity_request(
        self,
        text: str,
        metadata: Dict[str, Any],
        canon: Dict[str, Any],
    ) -> str:
        """Build continuity check request"""
        request = "**Chapter Text:**\n\n" + text + "\n\n"

        request += "**Canon Facts:**\n"
        if "characters" in canon:
            request += f"Characters: {', '.join(c.get('name', '') for c in canon['characters'])}\n"
        if "locations" in canon:
            request += f"Locations: {', '.join(l.get('name', '') for l in canon['locations'])}\n"
        if "timeline" in canon:
            request += f"Timeline: {canon['timeline']}\n"

        request += "\n**Check for continuity errors.**"
        return request

    async def _check_character_consistency(
        self,
        text: str,
        metadata: Dict[str, Any],
        canon: Dict[str, Any],
    ) -> List[QCIssue]:
        """
        Character Editor Agent

        Checks:
        - Out-of-character behavior
        - Voice consistency (dialogue)
        - Motivation alignment
        - Behavioral limits violated
        """
        prompt = self._build_character_prompt(canon)
        messages = [
            LLMMessage(role="system", content=prompt),
            LLMMessage(
                role="user",
                content=self._build_character_request(text, metadata, canon),
            ),
        ]

        llm = get_llm()
        config = LLMConfig(model="gpt-4", temperature=0.2, max_tokens=1000)

        try:
            response = await llm.complete(messages, config)
            issues = self._parse_qc_response(response.content, "character")
            return issues
        except Exception as e:
            print(f"Character check error: {e}")
            return []

    def _build_character_prompt(self, canon: Dict[str, Any]) -> str:
        """Build prompt for character agent"""
        return """You are the Character Editor in a writers' room.

Your job is to ensure character consistency:

**Behavioral consistency:**
- Actions align with goals, values, fears
- Character doesn't violate behavioral limits
- Choices match established personality

**Voice consistency:**
- Dialogue sounds like the character
- Speech patterns maintained
- Vocabulary appropriate

**Motivation:**
- Actions have clear motivations
- No random personality shifts
- Emotional reactions fit character

**Output format:**

ISSUE:
SEVERITY: blocker/warning/suggestion
DESCRIPTION: [what's out of character]
LOCATION: [dialogue or action]
FIX: [how to make it consistent]
---

Characters must feel like real, consistent people.
"""

    def _build_character_request(
        self,
        text: str,
        metadata: Dict[str, Any],
        canon: Dict[str, Any],
    ) -> str:
        """Build character check request"""
        request = "**Chapter Text:**\n\n" + text + "\n\n"

        request += "**Character Profiles:**\n"
        if "characters" in canon:
            for char in canon["characters"]:
                request += f"\n**{char.get('name', 'Unknown')}:**\n"
                request += f"Goals: {', '.join(char.get('goals', []))}\n"
                request += f"Values: {', '.join(char.get('values', []))}\n"
                request += f"Behavioral limits: {', '.join(char.get('behavioral_limits', []))}\n"

        request += "\n**Check for character consistency issues.**"
        return request

    async def _check_plot_logic(
        self,
        text: str,
        metadata: Dict[str, Any],
        canon: Dict[str, Any],
    ) -> List[QCIssue]:
        """
        Plot Editor Agent

        Checks:
        - Deus ex machina
        - Unearned victories
        - Logical gaps
        - Cause/effect breaks
        """
        prompt = self._build_plot_prompt()
        messages = [
            LLMMessage(role="system", content=prompt),
            LLMMessage(
                role="user",
                content=self._build_plot_request(text, metadata, canon),
            ),
        ]

        llm = get_llm()
        config = LLMConfig(model="gpt-4", temperature=0.2, max_tokens=1000)

        try:
            response = await llm.complete(messages, config)
            issues = self._parse_qc_response(response.content, "plot")
            return issues
        except Exception as e:
            print(f"Plot check error: {e}")
            return []

    def _build_plot_prompt(self) -> str:
        """Build prompt for plot agent"""
        return """You are the Plot Editor in a writers' room.

Your job is to ensure plot logic:

**Deus ex machina:**
- Solutions appearing from nowhere
- Convenient coincidences
- Unearned victories

**Cause and effect:**
- Events without clear causes
- Actions without consequences
- Logical gaps in reasoning

**Setup and payoff:**
- Powers/skills not established earlier
- Knowledge characters shouldn't have
- Items appearing without setup

**Stakes:**
- Tension deflating without reason
- Consequences not following through
- Threats that don't matter

**Output format:**

ISSUE:
SEVERITY: blocker/warning/suggestion
DESCRIPTION: [what's illogical]
LOCATION: [where in plot]
FIX: [how to fix logic]
---

Plot must be logical and earned.
"""

    def _build_plot_request(
        self,
        text: str,
        metadata: Dict[str, Any],
        canon: Dict[str, Any],
    ) -> str:
        """Build plot check request"""
        request = "**Chapter Text:**\n\n" + text + "\n\n"

        if "chapter_goal" in metadata:
            request += f"**Chapter Goal:** {metadata['chapter_goal']}\n"
        if "stakes" in metadata:
            request += f"**Stakes:** {metadata['stakes']}\n"

        request += "\n**Check for plot logic issues.**"
        return request

    # ===== Parsing and Scoring =====

    def _parse_qc_response(
        self,
        response: str,
        category: str,
    ) -> List[QCIssue]:
        """Parse LLM QC response into issues"""
        issues = []
        current_issue = {}

        lines = response.strip().split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("SEVERITY:"):
                current_issue["severity"] = line.split(":", 1)[1].strip().lower()

            elif line.startswith("DESCRIPTION:"):
                current_issue["description"] = line.split(":", 1)[1].strip()

            elif line.startswith("LOCATION:"):
                current_issue["location"] = line.split(":", 1)[1].strip()

            elif line.startswith("FIX:"):
                current_issue["fix"] = line.split(":", 1)[1].strip()

            elif line == "---" and current_issue:
                # Complete issue
                if "description" in current_issue:
                    issues.append(QCIssue(
                        category=category,
                        severity=current_issue.get("severity", "warning"),
                        description=current_issue["description"],
                        location=current_issue.get("location"),
                        suggested_fix=current_issue.get("fix"),
                    ))
                current_issue = {}

        # Handle last issue
        if current_issue and "description" in current_issue:
            issues.append(QCIssue(
                category=category,
                severity=current_issue.get("severity", "warning"),
                description=current_issue["description"],
                location=current_issue.get("location"),
                suggested_fix=current_issue.get("fix"),
            ))

        return issues

    def _calculate_qc_score(self, issues: List[QCIssue]) -> int:
        """
        Calculate QC score (0-100)

        100 = perfect, no issues
        0 = many blockers
        """
        if not issues:
            return 100

        # Penalty by severity
        penalties = {
            "blocker": 30,
            "warning": 10,
            "suggestion": 3,
        }

        total_penalty = sum(penalties.get(i.severity, 0) for i in issues)
        score = max(0, 100 - total_penalty)

        return score

    def _categorize_issues(self, issues: List[QCIssue]) -> Dict[str, int]:
        """Count issues by category"""
        counts = {}
        for issue in issues:
            counts[issue.category] = counts.get(issue.category, 0) + 1
        return counts
