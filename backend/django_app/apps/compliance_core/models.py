import hashlib
import json
import uuid
from django.db import models


class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    rule_version_id = models.BigIntegerField(db_index=True)
    input_hash = models.CharField(max_length=64, db_index=True)
    output_result = models.JSONField()
    execution_duration_ms = models.PositiveIntegerField()
    context = models.JSONField(default=dict)
    ledger_sequence_number = models.BigIntegerField(unique=True)
    merkle_hash = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = "compliance_decisions"
        indexes = [
            models.Index(fields=["rule_version_id", "timestamp"]),
            models.Index(fields=["correlation_id", "timestamp"]),
        ]


class Evidence(models.Model):
    CITATION_TYPES = (
        ("statute", "Statute"),
        ("case_law", "Case Law"),
        ("contract", "Contract"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(Decision, on_delete=models.PROTECT, related_name="evidence_items")
    citation_type = models.CharField(max_length=32, choices=CITATION_TYPES, db_index=True)
    source_url = models.URLField(blank=True)
    document_id = models.CharField(max_length=255, db_index=True)
    excerpt = models.TextField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4)
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "compliance_evidence"


def deterministic_json_hash(payload: dict) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
