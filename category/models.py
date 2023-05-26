from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    Category_name = models.CharField(max_length=50,unique=True)
    #slug is nothing but urls
    slug = models.SlugField(max_length=100,unique=True)
    description = models.TextField(max_length=255)
    #here the images will be uploaded to 'photos/categories'
    cat_image = models.ImageField(upload_to ='photos/categories/',blank=True)
 
    #django admin site usually add 's' to the models we create basically it pluralises
    #to make it right we use below code
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.slug])

    #string representation of model
    def __str__(self):
        return self.Category_name
        
