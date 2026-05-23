from django.db import models


FILE_TYPE_CHOICES = [
    ("pdf", "PDF"),
    ("xlsx", "XLSX"),
    ("csv", "CSV")
]

class DocumentModel(models.Model):
    file_name = models.CharField(
        verbose_name="file_name", 
        max_length=255, 
        blank=False, 
        null=False
    )
    file_type = models.CharField(
        verbose_name="file_type", 
        choices=FILE_TYPE_CHOICES
    )
    file_size = models.BinaryField(
        verbose_name="file_size", 
        blank=False, 
        null=False
    )
    seaweed_file_id = models.CharField(
        verbose_name="seaweed_file_id",
        max_length=255,
        blank=False,
        null=False,
        unique=True
    )
    file_content = models.CharField(
        verbose_name="file_content", 
        blank=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.file_name} ({self.seaweed_file_id})"
