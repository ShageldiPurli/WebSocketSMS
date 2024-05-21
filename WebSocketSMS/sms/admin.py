from django.contrib import admin

from sms.models import SMS


class SmsAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp')

    class Meta:
        model = SMS


# Register your models here.
admin.site.register(SMS, SmsAdmin)
