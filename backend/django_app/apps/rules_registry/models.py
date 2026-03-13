import hashlib
import uuid
from django.db import models


class Rule(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("deprecated", "Deprecated"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    jurisdiction = models.CharField(max_length=16, db_index=True)
    category = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft", db_index=True)
    current_version = models.ForeignKey(
        "RuleVersion", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rules"


class RuleVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    semantic_version = models.CharField(max_length=32)
    dsl_snapshot = models.JSONField()
    compiled_bytecode = models.BinaryField(null=True, blank=True)
    hash_sha256 = models.CharField(max_length=64, db_index=True)
    created_by = models.CharField(max_length=255)
    changelog = models.TextField(blank=True)
    effective_date = models.DateTimeField(null=True, blank=True)
    deprecated_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rule_versions"
        unique_together = (("rule", "version_number"), ("rule", "semantic_version"))

    def save(self, *args, **kwargs):
        if self.dsl_snapshot and not self.hash_sha256:
            self.hash_sha256 = hashlib.sha256(str(self.dsl_snapshot).encode("utf-8")).hexdigest()
        super().save(*args, **kwargs)
