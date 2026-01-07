"""
Canon Contracts Service

Validates hard rules that generation MUST respect
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from core.models.planner import CanonContract
from core.llm import get_llm, LLMMessage, LLMConfig


class ContractViolation:
    """
    Represents a contract violation
    """
    def __init__(
        self,
        contract_id: int,
        contract_name: str,
        violation_description: str,
        severity: str,
        suggested_fix: Optional[str] = None,
    ):
        self.contract_id = contract_id
        self.contract_name = contract_name
        self.violation_description = violation_description
        self.severity = severity
        self.suggested_fix = suggested_fix

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "contract_name": self.contract_name,
            "violation_description": self.violation_description,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }


class CanonContractsService:
    """
    Service for managing and validating Canon Contracts

    Canon Contracts are hard rules that:
    - Authors define (e.g., "Magic always costs blood")
    - AI generation MUST respect
    - QC validates before accepting content
    """

    def __init__(self, db: Session):
        self.db = db

    # ===== CRUD Operations =====

    def create_contract(
        self,
        project_id: int,
        name: str,
        description: str,
        constraint: str,
        rule_type: str,
        severity: str = "must",
        applies_to: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, str]]] = None,
    ) -> CanonContract:
        """
        Create a new canon contract

        Args:
            project_id: Project ID
            name: Contract name
            description: Human-readable description
            constraint: The actual rule (natural language)
            rule_type: world, character, magic, plot, style
            severity: must, should, prefer
            applies_to: Which entities this affects
            examples: Valid/invalid examples

        Returns:
            Created contract
        """
        # Generate validation prompt
        validation_prompt = self._generate_validation_prompt(
            constraint=constraint,
            rule_type=rule_type,
            examples=examples or [],
        )

        contract = CanonContract(
            project_id=project_id,
            name=name,
            description=description,
            constraint=constraint,
            rule_type=rule_type,
            severity=severity,
            applies_to=applies_to or {},
            validation_prompt=validation_prompt,
            examples=examples or [],
            active=True,
            violation_count=0,
        )

        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_contract(self, contract_id: int) -> Optional[CanonContract]:
        """Get contract by ID"""
        return self.db.query(CanonContract).filter(CanonContract.id == contract_id).first()

    def list_contracts(
        self,
        project_id: int,
        active_only: bool = True,
        rule_type: Optional[str] = None,
    ) -> List[CanonContract]:
        """
        List contracts for a project

        Args:
            project_id: Project ID
            active_only: Only return active contracts
            rule_type: Filter by rule type

        Returns:
            List of contracts
        """
        query = self.db.query(CanonContract).filter(
            CanonContract.project_id == project_id
        )

        if active_only:
            query = query.filter(CanonContract.active == True)

        if rule_type:
            query = query.filter(CanonContract.rule_type == rule_type)

        return query.all()

    def update_contract(
        self,
        contract_id: int,
        **updates
    ) -> CanonContract:
        """
        Update contract

        Args:
            contract_id: Contract ID
            **updates: Fields to update

        Returns:
            Updated contract
        """
        contract = self.get_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")

        for key, value in updates.items():
            if hasattr(contract, key):
                setattr(contract, key, value)

        # Regenerate validation prompt if constraint changed
        if "constraint" in updates or "examples" in updates:
            contract.validation_prompt = self._generate_validation_prompt(
                constraint=contract.constraint,
                rule_type=contract.rule_type,
                examples=contract.examples,
            )

        self.db.commit()
        self.db.refresh(contract)
        return contract

    def delete_contract(self, contract_id: int) -> bool:
        """
        Delete (deactivate) contract

        Args:
            contract_id: Contract ID

        Returns:
            True if deleted
        """
        contract = self.get_contract(contract_id)
        if not contract:
            return False

        # Soft delete - mark as inactive
        contract.active = False
        self.db.commit()
        return True

    # ===== Validation =====

    async def validate_text(
        self,
        project_id: int,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        rule_types: Optional[List[str]] = None,
    ) -> List[ContractViolation]:
        """
        Validate text against all active contracts

        Args:
            project_id: Project ID
            text: Text to validate (scene, chapter, etc.)
            context: Additional context (character names, location, etc.)
            rule_types: Only check specific rule types

        Returns:
            List of violations (empty if all contracts satisfied)
        """
        # Get active contracts
        contracts = self.list_contracts(
            project_id=project_id,
            active_only=True,
            rule_type=None,
        )

        # Filter by rule type if specified
        if rule_types:
            contracts = [c for c in contracts if c.rule_type in rule_types]

        # Validate against each contract
        violations = []
        for contract in contracts:
            violation = await self._validate_against_contract(
                contract=contract,
                text=text,
                context=context,
            )
            if violation:
                violations.append(violation)

        return violations

    async def _validate_against_contract(
        self,
        contract: CanonContract,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContractViolation]:
        """
        Validate text against a single contract using LLM

        Args:
            contract: Contract to validate against
            text: Text to check
            context: Additional context

        Returns:
            ContractViolation if violated, None if satisfied
        """
        # Build validation prompt
        messages = [
            LLMMessage(
                role="system",
                content=contract.validation_prompt,
            ),
            LLMMessage(
                role="user",
                content=self._build_validation_request(text, context, contract),
            ),
        ]

        # Call LLM
        llm = get_llm()
        config = LLMConfig(
            model="gpt-4",  # Use capable model for validation
            temperature=0.1,  # Low temperature for consistency
            max_tokens=500,
        )

        try:
            response = await llm.complete(messages, config)
            result = self._parse_validation_response(response.content)

            if result["violated"]:
                # Increment violation count
                contract.violation_count += 1
                self.db.commit()

                return ContractViolation(
                    contract_id=contract.id,
                    contract_name=contract.name,
                    violation_description=result["reason"],
                    severity=contract.severity,
                    suggested_fix=result.get("suggested_fix"),
                )

        except Exception as e:
            # Log error but don't fail validation
            print(f"Error validating contract {contract.id}: {e}")

        return None

    # ===== Helper Methods =====

    def _generate_validation_prompt(
        self,
        constraint: str,
        rule_type: str,
        examples: List[Dict[str, str]],
    ) -> str:
        """
        Generate LLM prompt for validating this contract

        Args:
            constraint: The rule
            rule_type: Type of rule
            examples: Valid/invalid examples

        Returns:
            Validation prompt
        """
        prompt = f"""You are a narrative consistency validator for a {rule_type} rule.

**Rule:** {constraint}

Your job is to check if a given text violates this rule.

"""

        if examples:
            prompt += "**Examples:**\n\n"
            for example in examples:
                if "valid" in example:
                    prompt += f"✓ VALID: {example['valid']}\n"
                if "invalid" in example:
                    prompt += f"✗ INVALID: {example['invalid']}\n"
            prompt += "\n"

        prompt += """**Instructions:**
1. Read the text carefully
2. Determine if it violates the rule
3. Respond in this exact format:

VIOLATED: yes/no
REASON: [explanation]
SUGGESTED_FIX: [how to fix it, if violated]

Be strict - if the rule says "always" or "never", even one violation counts.
"""

        return prompt

    def _build_validation_request(
        self,
        text: str,
        context: Optional[Dict[str, Any]],
        contract: CanonContract,
    ) -> str:
        """
        Build validation request message

        Args:
            text: Text to validate
            context: Additional context
            contract: Contract being validated

        Returns:
            Request message
        """
        request = "**Text to validate:**\n\n"
        request += text + "\n\n"

        if context:
            request += "**Context:**\n"
            for key, value in context.items():
                request += f"- {key}: {value}\n"
            request += "\n"

        request += f"**Rule to check:** {contract.constraint}\n\n"
        request += "Does this text violate the rule?"

        return request

    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM validation response

        Args:
            response: LLM response text

        Returns:
            Parsed result
        """
        result = {
            "violated": False,
            "reason": "",
            "suggested_fix": None,
        }

        lines = response.strip().split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("VIOLATED:"):
                violated_str = line.split(":", 1)[1].strip().lower()
                result["violated"] = violated_str == "yes"

            elif line.startswith("REASON:"):
                result["reason"] = line.split(":", 1)[1].strip()

            elif line.startswith("SUGGESTED_FIX:"):
                result["suggested_fix"] = line.split(":", 1)[1].strip()

        return result

    # ===== Bulk Validation =====

    async def validate_chapter(
        self,
        project_id: int,
        chapter_content: str,
        chapter_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate entire chapter against contracts

        Args:
            project_id: Project ID
            chapter_content: Full chapter text
            chapter_metadata: Chapter info (number, POV character, etc.)

        Returns:
            Validation report
        """
        violations = await self.validate_text(
            project_id=project_id,
            text=chapter_content,
            context=chapter_metadata,
        )

        return {
            "valid": len(violations) == 0,
            "violation_count": len(violations),
            "violations": [v.to_dict() for v in violations],
            "severity_breakdown": self._count_by_severity(violations),
        }

    def _count_by_severity(
        self,
        violations: List[ContractViolation],
    ) -> Dict[str, int]:
        """Count violations by severity"""
        counts = {"must": 0, "should": 0, "prefer": 0}
        for v in violations:
            if v.severity in counts:
                counts[v.severity] += 1
        return counts
