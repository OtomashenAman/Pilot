import hashlib
import json
import uuid

from django.db import models
from django.utils import timezone


class Rule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=50, db_index=True)
    description = models.TextField(blank=True)
    current_version = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rules"


class RuleVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT, related_name="versions")
    version = models.CharField(max_length=20)
    dsl_definition = models.JSONField()
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    jurisdiction = models.CharField(max_length=50, db_index=True)
    is_active = models.BooleanField(default=True)
    supersedes = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="superseded_by")
    content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rule_versions"
        unique_together = (("rule", "version"),)
        indexes = [
            models.Index(fields=["rule", "effective_from"], name="idx_rule_effective_from"),
            models.Index(fields=["jurisdiction", "effective_from"], name="idx_jurisdiction_effective"),
        ]

    def compute_content_hash(self) -> str:
        payload = {
            "rule_id": str(self.rule_id),
            "version": self.version,
            "dsl_definition": self.dsl_definition,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "effective_to": self.effective_to.isoformat() if self.effective_to else None,
            "jurisdiction": self.jurisdiction,
        }
        canon = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canon).hexdigest()

    def clean(self):
        if self.effective_to and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be greater than effective_from")

    def save(self, *args, **kwargs):
        if not self.content_hash:
            self.content_hash = self.compute_content_hash()
        super().save(*args, **kwargs)
        if self.is_active:
            Rule.objects.filter(id=self.rule_id).update(current_version=self.version, updated_at=timezone.now())
