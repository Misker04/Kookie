from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    material = models.CharField(max_length=50, blank=True, null=True)  # E.g., 'cotton', 'leather'
    style = models.CharField(max_length=50, blank=True, null=True)  # E.g., 'sneakers', 'boots'
    use_case = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Promotion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.title

class Feedback(models.Model):
    comments = models.TextField()  # or CharField depending on length
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.created_at}"
    
class StoreSection(models.Model):
    name = models.CharField(max_length=100, unique=True)  # The name of the store section
    description = models.TextField(blank=True, null=True)  # Optional description of the section
    location = models.CharField(max_length=200, blank=True, null=True)  # Optional location of the section

    def __str__(self):
        return self.name

class Support(models.Model):
    query = models.CharField(max_length=255)
    response = models.TextField()

    def __str__(self):
        return self.query