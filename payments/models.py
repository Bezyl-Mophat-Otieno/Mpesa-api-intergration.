from django.db import models

# Create your models here.

class MPESATransaction(models.Model):
    transaction_id = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.phone_number} - {self.amount} - {self.status}"