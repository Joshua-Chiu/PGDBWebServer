from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Configuration(models.Model):
    principal_signature = models.ImageField(upload_to='export/uploads', default='export/uploads/principal-signature.png')
    login_failure_limit = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)], default=3)

    se_help_text = models.CharField(max_length=50, verbose_name='Service Help Text', default='Service')
    at_help_text = models.CharField(max_length=30, verbose_name='Athletics Help Text', default='Athletics')
    fa_help_text = models.CharField(max_length=30, verbose_name='Fine Arts Help Text', default='Fine Arts')

    def save(self, *args, **kwargs):
        if not self.pk and Configuration.objects.exists():
            # if you'll not check for self.pk then error will also raised in update of exists model
            raise ValidationError('There can be only one Configuration instance')
        return super(Configuration, self).save(*args, **kwargs)

    def __str__(self):
        return "Point Grey Database System Configurations"
