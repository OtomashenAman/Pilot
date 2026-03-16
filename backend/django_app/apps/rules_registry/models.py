import re
import uuid

from django.core.exceptions import ValidationError
from django.db import models


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class RuleVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_key = models.CharField(max_length=100, db_index=True)
    version = models.CharField(max_length=20)
    ast_json = models.JSONField(default=dict)
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=100)
    git_commit_hash = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rule_versions"
        unique_together = (("rule_key", "version"),)
        indexes = [models.Index(fields=["rule_key", "effective_from"]) ]

    def clean(self):
        if not SEMVER_RE.match(self.version):
            raise ValidationError({"version": "version must follow semantic versioning MAJOR.MINOR.PATCH"})
        if self.effective_to and self.effective_to <= self.effective_from:
            raise ValidationError({"effective_to": "effective_to must be greater than effective_from"})
