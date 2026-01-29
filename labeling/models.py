from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings


# Create your models here.
class User(AbstractUser):
    
    ROLE_CHOICES = (
        ('contributor', 'Contributeur'),
        ('validator', 'Validateur'),
        ('admin', 'Administrateur'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='contributor')

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"

class DataItem(models.Model):
    TYPES = (('image', 'Image'), ('text', 'Texte'), ('audio', 'Audio'))
    content = models.TextField(help_text='url de l\'element ou contenu textuel')
    data_type = models.CharField(max_length=10, choices=TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.data_type} - {self.id}"

    objects = models.Manager()
    
class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

    objects = models.Manager()
    
class Annotation(models.Model):
    item = models.ForeignKey(DataItem, on_delete=models.CASCADE, related_name='annotations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('item', 'user')

    objects = models.Manager()
        
class Validation(models.Model):
    annotation = models.OneToOneField(Annotation, on_delete=models.CASCADE, related_name='validation')
    validator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_approved = models.BooleanField( default=True)
    feedback = models.TextField(blank=True, null=True)
    validated_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    