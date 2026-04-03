import hashlib
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RuleVersion(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_DEPRECATED = "deprecated"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_DEPRECATED, "Deprecated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_id = models.UUIDField(db_index=True)
    version = models.CharField(max_length=20)
    definition = models.JSONField()
    bytecode = models.BinaryField(blank=True, null=True)
    hash = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("rule_id", "version")
        indexes = [models.Index(fields=["rule_id", "status"])]

    def save(self, *args, **kwargs):
        if not self.hash and self.definition is not None:
            payload = str(self.definition).encode("utf-8")
            self.hash = hashlib.sha256(payload).hexdigest()
        super().save(*args, **kwargs)


class DecisionLedger(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_version = models.ForeignKey(RuleVersion, on_delete=models.PROTECT, related_name="ledger_entries")
    tenant_id = models.UUIDField(db_index=True)
    input_hash = models.CharField(max_length=64, db_index=True)
    output = models.JSONField()
    evidence_refs = models.JSONField(default=list)
    merkle_root = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    chain_hash = models.CharField(max_length=64, db_index=True)
    signature = models.BinaryField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant_id", "created_at"]),
            models.Index(fields=["rule_version", "created_at"]),
        ]


class Evidence(TimeStampedModel):
    SOURCE_DOCUMENT = "document"
    SOURCE_API = "api"
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = [
        (SOURCE_DOCUMENT, "Document"),
        (SOURCE_API, "API"),
        (SOURCE_MANUAL, "Manual"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ledger_entry = models.ForeignKey(DecisionLedger, on_delete=models.CASCADE, related_name="evidence")
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    storage_path = models.CharField(max_length=512)
    content_hash = models.CharField(max_length=64, db_index=True)
    metadata = models.JSONField(default=dict)
    retention_until = models.DateTimeField()
