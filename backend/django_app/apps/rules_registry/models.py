import uuid
from django.db import models


class Rule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RuleSet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    rules = models.ManyToManyField("compliance_core.RuleVersion", related_name="rule_sets")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "version")


class RuleBranch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=100)
    base_version = models.CharField(max_length=20, blank=True)
    head_version = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("rule", "name")
