from django.db import models


# Create your models here.
class SMS(models.Model):
    phone_number = models.CharField(max_length=10)
    otp = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        mod = SMS.objects.filter(phone_number=self.phone_number)
        if mod:
            mod.delete()
        super(SMS, self).save(*args, **kwargs)

    def __str__(self):
        return self.phone_number
