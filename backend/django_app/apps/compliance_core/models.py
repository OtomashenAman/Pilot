import hashlib
import json
import uuid

from django.db import models


class Evidence(models.Model):
    EVIDENCE_TYPES = (
        ("uploaded_document", "Uploaded Document"),
        ("api_response", "API Response"),
        ("calculated_field", "Calculated Field"),
        ("manual_review", "Manual Review"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evidence_type = models.CharField(max_length=50, choices=EVIDENCE_TYPES)
    source_uri = models.CharField(max_length=500, blank=True)
    content_hash = models.CharField(max_length=64, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "evidence"


class DecisionLedger(models.Model):
    DECISION_OUTPUTS = (("pass", "Pass"), ("fail", "Fail"), ("review", "Review"), ("override", "Override"))

    id = models.BigAutoField(primary_key=True)
    decision_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    rule_version_id = models.UUIDField(db_index=True)
    input_hash = models.CharField(max_length=64, db_index=True)
    output = models.CharField(max_length=20, choices=DECISION_OUTPUTS)
    output_result = models.JSONField(default=dict)
    evidence_refs = models.ManyToManyField(Evidence, related_name="decisions", blank=True)
    previous_hash = models.CharField(max_length=64, blank=True)
    current_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "decision_ledger"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["rule_version_id", "created_at"]),
        ]

    @staticmethod
    def canonical_json(data: dict) -> str:
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def compute_input_hash(cls, context: dict) -> str:
        return hashlib.sha256(cls.canonical_json(context).encode("utf-8")).hexdigest()

    @classmethod
    def compute_chain_hash(cls, previous_hash: str, payload: dict) -> str:
        preimage = f"{previous_hash}:{cls.canonical_json(payload)}"
        return hashlib.sha256(preimage.encode("utf-8")).hexdigest()
