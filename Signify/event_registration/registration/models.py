from django.db import models

# Create your models here.
class Attendee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    company = models.CharField(max_length=100)
    qr_code_value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} - {self.company}"

def get_latest_template():
    return NameTagTemplate.objects.latest('id').template_file.url
class NameTagTemplate(models.Model):
    template = models.ImageField(upload_to='name_tag_templates/')

    def __str__(self):
        return f"Template {self.id}"