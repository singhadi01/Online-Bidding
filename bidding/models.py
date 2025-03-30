from django.db import models
from django.contrib.auth.models import User
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    state = models.CharField(max_length=50)
    aadhaar_number = models.CharField(max_length=12, unique=True)  # Ensure uniqueness
    gmail = models.EmailField(unique=True) 
    mobile_number = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.user.username

def generate_unique_code():
    """Generate a random unique 6-character alphanumeric code."""
    while True:
        new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Item.objects.filter(unique_code=new_code).exists():
            return new_code

class Item(models.Model):
    STATUS_CHOICES = [
        ('live', 'Live'),
        ('closed', 'Closed'),
        ('upcoming', 'Open Soon'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.FloatField()
    unique_code = models.CharField(max_length=6, unique=True, editable=False)  # Not editable by user
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')

    def save(self, *args, **kwargs):
        """Auto-generate code before saving."""
        if not self.unique_code:  
            self.unique_code = generate_unique_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.unique_code} - {self.status}"

class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"
