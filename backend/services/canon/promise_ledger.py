"""
Promise/Payoff Ledger Service

Automatic detection and tracking of narrative promises

Solves the #1 problem in long novels: abandoned promises
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.models.canon import Promise
from core.llm import get_llm, LLMMessage, LLMConfig


class DetectedPromise:
    """
    A promise detected in text
    """
    def __init__(
        self,
        setup_description: str,
        payoff_required: str,
        confidence: float,
        chapter: int,
        scene: Optional[int] = None,
        suggested_deadline: Optional[int] = None,
    ):
        self.setup_description = setup_description
        self.payoff_required = payoff_required
        self.confidence = confidence
        self.chapter = chapter
        self.scene = scene
        self.suggested_deadline = suggested_deadline

    def to_dict(self) -> Dict[str, Any]:
        return {
            "setup_description": self.setup_description,
            "payoff_required": self.payoff_required,
            "confidence": self.confidence,
            "chapter": self.chapter,
            "scene": self.scene,
            "suggested_deadline": self.suggested_deadline,
        }


class PromiseLedgerService:
    """
    Service for managing Promise/Payoff tracking

    Features:
    - Auto-detect promises in text (Chekhov's Gun, foreshadowing, etc.)
    - Track promise status (open, fulfilled, abandoned)
    - Warn when deadlines approach
    - Validate payoffs actually fulfill promises
    """

    def __init__(self, db: Session):
        self.db = db

    # ===== Auto-Detection =====

    async def detect_promises(
        self,
        text: str,
        chapter: int,
        scene: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectedPromise]:
        """
        Automatically detect narrative promises in text

        Args:
            text: Text to analyze (scene, chapter, etc.)
            chapter: Chapter number
            scene: Scene number
            context: Additional context

        Returns:
            List of detected promises
        """
        # Build detection prompt
        messages = [
            LLMMessage(
                role="system",
                content=self._build_detection_prompt(),
            ),
            LLMMessage(
                role="user",
                content=self._build_detection_request(text, context),
            ),
        ]

        # Call LLM
        llm = get_llm()
        config = LLMConfig(
            model="gpt-4",
            temperature=0.3,  # Moderate creativity
            max_tokens=1500,
        )

        try:
            response = await llm.complete(messages, config)
            promises = self._parse_detection_response(
                response.content,
                chapter,
                scene,
            )
            return promises

        except Exception as e:
            print(f"Error detecting promises: {e}")
            return []

    def _build_detection_prompt(self) -> str:
        """Build system prompt for promise detection"""
        return """You are a narrative structure analyzer specializing in detecting narrative promises.

**What is a narrative promise?**
A promise is any setup that creates reader expectation of future payoff:
- Chekhov's Gun: "If you show a gun in Act 1, it must fire by Act 3"
- Foreshadowing: Hints at future events
- Character goals: "I will find my father's killer"
- Mysteries: "What's behind the locked door?"
- Threats: "The dragon will return"
- Prophecies, curses, vows, secrets revealed

**Your job:**
1. Read the text carefully
2. Identify ALL narrative promises
3. For each promise, specify:
   - What was set up (the promise)
   - What payoff is required
   - Confidence (0-100)
   - Suggested deadline (chapters from now)

**Output format:**
For each promise, output exactly:

PROMISE:
SETUP: [What was set up]
PAYOFF_REQUIRED: [What must happen to fulfill this]
CONFIDENCE: [0-100]
SUGGESTED_DEADLINE: [number of chapters]
---

Be thorough - missing promises breaks narrative structure.
Be precise - vague payoffs are useless.
"""

    def _build_detection_request(
        self,
        text: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Build detection request"""
        request = "**Text to analyze:**\n\n"
        request += text + "\n\n"

        if context:
            request += "**Context:**\n"
            for key, value in context.items():
                request += f"- {key}: {value}\n"
            request += "\n"

        request += "Identify all narrative promises in this text."
        return request

    def _parse_detection_response(
        self,
        response: str,
        chapter: int,
        scene: Optional[int],
    ) -> List[DetectedPromise]:
        """Parse LLM detection response"""
        promises = []
        current_promise = {}

        lines = response.strip().split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("SETUP:"):
                current_promise["setup"] = line.split(":", 1)[1].strip()

            elif line.startswith("PAYOFF_REQUIRED:"):
                current_promise["payoff"] = line.split(":", 1)[1].strip()

            elif line.startswith("CONFIDENCE:"):
                try:
                    current_promise["confidence"] = float(line.split(":", 1)[1].strip())
                except:
                    current_promise["confidence"] = 50.0

            elif line.startswith("SUGGESTED_DEADLINE:"):
                try:
                    deadline_str = line.split(":", 1)[1].strip()
                    deadline = int(deadline_str.split()[0])  # Extract number
                    current_promise["deadline"] = chapter + deadline
                except:
                    current_promise["deadline"] = None

            elif line == "---" and current_promise:
                # Complete promise
                if "setup" in current_promise and "payoff" in current_promise:
                    promises.append(DetectedPromise(
                        setup_description=current_promise["setup"],
                        payoff_required=current_promise["payoff"],
                        confidence=current_promise.get("confidence", 50.0),
                        chapter=chapter,
                        scene=scene,
                        suggested_deadline=current_promise.get("deadline"),
                    ))
                current_promise = {}

        # Handle last promise if no trailing ---
        if current_promise and "setup" in current_promise and "payoff" in current_promise:
            promises.append(DetectedPromise(
                setup_description=current_promise["setup"],
                payoff_required=current_promise["payoff"],
                confidence=current_promise.get("confidence", 50.0),
                chapter=chapter,
                scene=scene,
                suggested_deadline=current_promise.get("deadline"),
            ))

        return promises

    # ===== Promise Management =====

    def get_open_promises(
        self,
        project_id: int,
        before_chapter: Optional[int] = None,
    ) -> List[Promise]:
        """
        Get all open (unfulfilled) promises

        Args:
            project_id: Project ID
            before_chapter: Only promises from before this chapter

        Returns:
            List of open promises
        """
        query = self.db.query(Promise).filter(
            Promise.project_id == project_id,
            Promise.status == "open",
        )

        if before_chapter:
            query = query.filter(Promise.setup_chapter < before_chapter)

        return query.order_by(Promise.setup_chapter).all()

    def get_promises_near_deadline(
        self,
        project_id: int,
        current_chapter: int,
        lookahead: int = 3,
    ) -> List[Promise]:
        """
        Get promises approaching their deadline

        Args:
            project_id: Project ID
            current_chapter: Current chapter
            lookahead: Chapters ahead to check

        Returns:
            Promises with deadlines within lookahead
        """
        deadline_threshold = current_chapter + lookahead

        promises = self.db.query(Promise).filter(
            Promise.project_id == project_id,
            Promise.status == "open",
            Promise.payoff_deadline.isnot(None),
            Promise.payoff_deadline <= deadline_threshold,
        ).all()

        return promises

    def get_overdue_promises(
        self,
        project_id: int,
        current_chapter: int,
    ) -> List[Promise]:
        """
        Get promises past their deadline

        Args:
            project_id: Project ID
            current_chapter: Current chapter

        Returns:
            Overdue promises
        """
        promises = self.db.query(Promise).filter(
            Promise.project_id == project_id,
            Promise.status == "open",
            Promise.payoff_deadline.isnot(None),
            Promise.payoff_deadline < current_chapter,
        ).all()

        return promises

    # ===== Payoff Validation =====

    async def validate_payoff(
        self,
        promise_id: int,
        payoff_text: str,
        payoff_chapter: int,
        payoff_scene: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Validate that payoff actually fulfills promise

        Args:
            promise_id: Promise ID
            payoff_text: Text containing proposed payoff
            payoff_chapter: Chapter number
            payoff_scene: Scene number

        Returns:
            Validation result
        """
        promise = self.db.query(Promise).filter(Promise.id == promise_id).first()
        if not promise:
            return {"valid": False, "error": "Promise not found"}

        # Build validation prompt
        messages = [
            LLMMessage(
                role="system",
                content=self._build_payoff_validation_prompt(),
            ),
            LLMMessage(
                role="user",
                content=self._build_payoff_validation_request(promise, payoff_text),
            ),
        ]

        # Call LLM
        llm = get_llm()
        config = LLMConfig(
            model="gpt-4",
            temperature=0.2,
            max_tokens=500,
        )

        try:
            response = await llm.complete(messages, config)
            result = self._parse_payoff_validation(response.content)

            if result["valid"]:
                # Update promise as fulfilled
                promise.status = "fulfilled"
                promise.payoff_chapter = payoff_chapter
                promise.payoff_scene = payoff_scene
                promise.payoff_description = payoff_text[:500]  # Truncate
                promise.validated = result
                self.db.commit()

            return result

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _build_payoff_validation_prompt(self) -> str:
        """Build payoff validation prompt"""
        return """You are validating that a narrative payoff fulfills its promise.

**Chekhov's Gun principle:**
"If you show a gun in Act 1, it must fire by Act 3"

**Your job:**
1. Read the original promise (setup)
2. Read the proposed payoff
3. Determine if the payoff truly fulfills the promise

**Output format:**

VALID: yes/no
REASON: [explanation]
COMPLETENESS: [0-100, how well it fulfills the promise]
SUGGESTIONS: [optional improvements]

Be strict - vague or partial payoffs should not pass.
"""

    def _build_payoff_validation_request(
        self,
        promise: Promise,
        payoff_text: str,
    ) -> str:
        """Build payoff validation request"""
        request = "**Original Promise:**\n"
        request += f"Setup (Chapter {promise.setup_chapter}): {promise.setup_description}\n"
        request += f"Required payoff: {promise.payoff_required}\n\n"

        request += "**Proposed Payoff:**\n"
        request += payoff_text + "\n\n"

        request += "Does this payoff fulfill the promise?"
        return request

    def _parse_payoff_validation(self, response: str) -> Dict[str, Any]:
        """Parse payoff validation response"""
        result = {
            "valid": False,
            "reason": "",
            "completeness": 0,
            "suggestions": None,
        }

        lines = response.strip().split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("VALID:"):
                valid_str = line.split(":", 1)[1].strip().lower()
                result["valid"] = valid_str == "yes"

            elif line.startswith("REASON:"):
                result["reason"] = line.split(":", 1)[1].strip()

            elif line.startswith("COMPLETENESS:"):
                try:
                    result["completeness"] = int(line.split(":", 1)[1].strip())
                except:
                    result["completeness"] = 0

            elif line.startswith("SUGGESTIONS:"):
                result["suggestions"] = line.split(":", 1)[1].strip()

        return result

    # ===== Reporting =====

    def get_ledger_report(
        self,
        project_id: int,
        current_chapter: int,
    ) -> Dict[str, Any]:
        """
        Get comprehensive promise ledger report

        Args:
            project_id: Project ID
            current_chapter: Current chapter

        Returns:
            Full report on promise status
        """
        open_promises = self.get_open_promises(project_id)
        near_deadline = self.get_promises_near_deadline(project_id, current_chapter)
        overdue = self.get_overdue_promises(project_id, current_chapter)

        fulfilled = self.db.query(Promise).filter(
            Promise.project_id == project_id,
            Promise.status == "fulfilled",
        ).count()

        abandoned = self.db.query(Promise).filter(
            Promise.project_id == project_id,
            Promise.status == "abandoned",
        ).count()

        return {
            "total_promises": len(open_promises) + fulfilled + abandoned,
            "open_count": len(open_promises),
            "fulfilled_count": fulfilled,
            "abandoned_count": abandoned,
            "near_deadline_count": len(near_deadline),
            "overdue_count": len(overdue),
            "health_score": self._calculate_health_score(
                len(open_promises), fulfilled, abandoned, len(overdue)
            ),
            "warnings": self._generate_warnings(near_deadline, overdue),
        }

    def _calculate_health_score(
        self,
        open_count: int,
        fulfilled: int,
        abandoned: int,
        overdue: int,
    ) -> int:
        """
        Calculate promise ledger health score (0-100)

        100 = perfect (all fulfilled, none overdue)
        0 = disaster (many abandoned, many overdue)
        """
        total = open_count + fulfilled + abandoned
        if total == 0:
            return 100

        # Base score from fulfillment rate
        fulfillment_rate = fulfilled / total if total > 0 else 0
        score = fulfillment_rate * 100

        # Penalty for overdue
        if open_count > 0:
            overdue_penalty = (overdue / open_count) * 30
            score -= overdue_penalty

        # Penalty for abandoned
        abandoned_penalty = (abandoned / total) * 20
        score -= abandoned_penalty

        return max(0, min(100, int(score)))

    def _generate_warnings(
        self,
        near_deadline: List[Promise],
        overdue: List[Promise],
    ) -> List[str]:
        """Generate warning messages"""
        warnings = []

        if overdue:
            warnings.append(
                f"⚠️ {len(overdue)} promise(s) are OVERDUE (past deadline without payoff)"
            )

        if near_deadline:
            warnings.append(
                f"⏰ {len(near_deadline)} promise(s) approaching deadline in next 3 chapters"
            )

        return warnings
