from django.db import models
from django.utils.text import slugify
from unidecode import unidecode


# Create your models here.

class ProductCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            title_in_latin = unidecode(self.title)
            self.slug = slugify(title_in_latin)

        original_slug = self.slug
        queryset = ProductCategory.objects.filter(slug=self.slug)
        counter = 1
        while queryset.exists():
            self.slug = f"{original_slug}-{counter}"
            queryset = ProductCategory.objects.filter(slug=self.slug)
            counter += 1

        super(ProductCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "دسته بندی"
        verbose_name = "دسته بندی ها"


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    categories = models.ManyToManyField(ProductCategory, related_name='products')
    discount_price = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            title_in_latin = unidecode(self.title)
            self.slug = slugify(title_in_latin)

        original_slug = self.slug
        queryset = Product.objects.filter(slug=self.slug)
        counter = 1
        while queryset.exists():
            self.slug = f"{original_slug}-{counter}"
            queryset = Product.objects.filter(slug=self.slug)
            counter += 1

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ماژول محصولات'
        verbose_name_plural = "محصول"
        verbose_name = "محصولات"
