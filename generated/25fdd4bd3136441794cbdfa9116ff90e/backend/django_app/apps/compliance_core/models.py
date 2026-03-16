import hashlib
import json
import uuid

from django.db import models
from django.utils import timezone


class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_id = models.CharField(max_length=255, db_index=True)
    rule_version_id = models.UUIDField(db_index=True)
    input_payload = models.JSONField()
    output_decision = models.JSONField()
    evidence_map = models.JSONField(default=dict)
    previous_hash = models.CharField(max_length=64, null=True, blank=True)
    ledger_hash = models.CharField(max_length=64, unique=True, db_index=True)
    evaluated_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "decisions"
        indexes = [
            models.Index(fields=["entity_id", "evaluated_at"], name="idx_entity_time"),
            models.Index(fields=["rule_version_id", "evaluated_at"], name="idx_rule_time"),
        ]
        ordering = ["-evaluated_at"]

    def compute_ledger_hash(self) -> str:
        payload = {
            "id": str(self.id),
            "entity_id": self.entity_id,
            "rule_version_id": str(self.rule_version_id),
            "input_payload": self.input_payload,
            "output_decision": self.output_decision,
            "evidence_map": self.evidence_map,
            "previous_hash": self.previous_hash,
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None,
        }
        canon = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canon).hexdigest()

    def save(self, *args, **kwargs):
        if not self.ledger_hash:
            self.ledger_hash = self.compute_ledger_hash()
        super().save(*args, **kwargs)


class Evidence(models.Model):
    SOURCE_API = "api"
    SOURCE_DOCUMENT = "document"
    SOURCE_MANUAL = "manual"
    SOURCE_SYSTEM = "system"
    SOURCE_TYPES = [
        (SOURCE_API, "API"),
        (SOURCE_DOCUMENT, "Document"),
        (SOURCE_MANUAL, "Manual"),
        (SOURCE_SYSTEM, "System"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(Decision, on_delete=models.PROTECT, related_name="evidence_items")
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    reference_id = models.CharField(max_length=255)
    field_path = models.CharField(max_length=255, blank=True)
    data_hash = models.CharField(max_length=64)
    confidence_score = models.FloatField()
    captured_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "evidence"
        indexes = [
            models.Index(fields=["reference_id"], name="idx_evidence_ref"),
            models.Index(fields=["captured_at"], name="idx_evidence_time"),
        ]
