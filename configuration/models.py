from django.core.exceptions import ValidationError
from django.db import models


class Configuration(models.Model):
    principal_signature = models.ImageField(upload_to='export/uploads', default='export/uploads/no-img.png')

    def save(self, *args, **kwargs):
        if not self.pk and Configuration.objects.exists():
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError('There can be only one Configuration instance')
        return super(Configuration, self).save(*args, **kwargs)

    def __str__(self):
        return "Point Grey Database System Configurations"
