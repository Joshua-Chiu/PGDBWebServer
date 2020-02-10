from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from data.models import LoggedAction


class Configuration(models.Model):
    principal_signature = models.ImageField(upload_to='export/uploads', default='export/uploads/signbox.png',
                                            help_text="Please upload a PNG file with dimensions 500 x 250\n"
                                                      "A blank signature requires the upload of a white .png")
    login_failure_limit = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)], default=3)

    se_help_text = models.CharField(max_length=100, verbose_name='Service Help Text', default='Service')
    at_help_text = models.CharField(max_length=100, verbose_name='Athletics Help Text', default='Athletics')
    fa_help_text = models.CharField(max_length=100, verbose_name='Fine Arts Help Text', default='Fine Arts')

    def save(self, user=None, *args, **kwargs):
        if not self.pk and Configuration.objects.exists():
            # if you'll not check for self.pk then error will also raised in update of exists model
            raise ValidationError('There can be only one Configuration instance')
        else:
            log = LoggedAction(user=user, message=f"System Configuration: Changed")
            log.save()
        return super(Configuration, self).save(*args, **kwargs)

    def __str__(self):
        return "Point Grey Database System Configurations"
