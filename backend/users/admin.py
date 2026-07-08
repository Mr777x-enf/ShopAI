from django.contrib import admin

# Register your models here.
# users/admin.py

from django.contrib import admin


from .models import User, Address, Product, Category, Brand, ProductImage, Review, ProductEmbedding, ProductVariant

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ProductImage) 
admin.site.register(Review)
admin.site.register(ProductEmbedding)
admin.site.register(ProductVariant)