from django.db import models
from django.utils import timezone

# Create your models here.
class Company(models.Model):
    ticker = models.CharField(primary_key=True, max_length = 10)
    name = models.CharField(unique=True, max_length = 255)
    logo_img = models.TextField(null=True, blank=True)
    common_name = models.CharField(null=True, blank=True, max_length = 100)
    last_blank_day = models.DateField(null=True, blank=True)

    p_neg = models.IntegerField(null=True, blank=True)
    p_ind = models.IntegerField(null=True, blank=True)
    p_pos = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

class Article(models.Model):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255)
    date = models.DateField(default = timezone.now().date())
    
    subtitle = models.TextField(null=True, blank=True)
    source = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)

    sentiment = models.CharField(max_length=1, null=True, blank=True)
    isFin = models.BooleanField(default=True)
    review = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)
    class Meta :
        unique_together = ('company_id', 'title') #since django doesnt support weak entity relations, this is the next best thing
    
class Price(models.Model):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(default = timezone.now().date())
    price = models.FloatField(default=0.0)
    change_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return ': $'.join([str(self.date),str(self.price), str(self.change_pct)])
    class Meta :
        unique_together = ('company_id', 'date')