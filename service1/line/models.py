from django.db import models

class KnowledgeGraph(models.Model):
    RULE_CHOICES = (
        ('filter', 'For Filtering'),
        ('route', 'For Routing / Ask to Who'),
    )
    purpose = models.CharField(max_length=100, choices=RULE_CHOICES)
    title = models.CharField(max_length=100)
    json = models.TextField()
    owner = models.CharField(max_length=100, null=True)
    class Meta:
        verbose_name_plural = "Knowledge Graphs"
    def __str__(self):
        return f"Rule: {self.purpose}, Json: {self.json[:50]}..."

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    # is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "FAQs"
    def __str__(self):
        return f"Q: {self.question[:50]}... A: {self.answer[:50]}..."

class History(models.Model):
    username = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "History"
    def __str__(self):
        return f"U: {self.username} Q: {self.question[:50]}... A: {self.answer[:50]}..."

class Rule(models.Model):
    rule = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Rules"
