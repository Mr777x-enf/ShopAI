import uuid 
from django.db import models 
from django.core.validators import MinValueValidator,MaxValueValidator 


from users.models.user import User
from pgvector.django import VectorField 
from pgvector.django import VectorField

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) 
    slug = models.SlugField(max_length=100, unique=True) 
    description = models.TextField(blank=True, null=True) 
    image = models.ImageField(upload_to='categories/', blank=True, null=True) 

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children') 


    is_active = models.BooleanField(default=True) 
    order = models.PositiveIntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'
        ordering = ['order', 'name'] 

    def __str__(self):
        return self.name 
    

    def save(self, *args, **kwargs):
        if not self.slug:
             self.slug = slugify(self.name)
        super().save(*args, **kwargs ) 
    

    @property

    def full_path(self):
        """Return the full category path as a string, e.g., 'Parent > Child'."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name 
class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) 
    slug = models.SlugField(max_length=100, unique=True) 
    description = models.TextField(blank=True, null=True) 
    image = models.ImageField(upload_to='brands/', blank=True, null=True) 

    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        db_table = 'brands'
        ordering = ['name'] 

    def __str__(self):
        return self.name 
    

    def save(self, *args, **kwargs):
        if not self.slug:
             self.slug = slugify(self.name)
        super().save(*args, **kwargs )

class Product(models.Model):
    class status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active' 
        INACTIVE = 'INACTIVE', 'Inactive' 
        OUT_OF_STOCK = 'OUT_OF_STOCK', 'Out of Stock'
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255) 
    slug = models.SlugField(max_length=255, unique=True) 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products') 

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')  
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]) 
    original_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)  
    stock_quantity = models.PositiveIntegerField(default=0) 
    sku = models.CharField(max_length=100, unique=True) 
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True) 
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True, null=True) 
    description = models.TextField(blank=True, null=True) 
    specifications = models.JSONField(blank=True, null=True) 
    tags = models.JSONField(default=list, blank=True) 
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True) 

    search_text = models.TextField(blank=True, help_text="Text used for search indexing, not displayed to users.") 

    status = models.CharField(max_length=20, choices=status.choices, default=status.DRAFT)
    is_featured = models.BooleanField(default=False)  
    is_best_seller = models.BooleanField(default=False)  
    is_new_arrival = models.BooleanField(default=False)  

    #count 

    view_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0) 
    rating_count = models.PositiveIntegerField(default=0) 
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], default=0) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    published_at = models.DateTimeField(blank=True, null=True) 

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ['-created_at'] 



        indexes = [
            models.Index(fields = ["status", "is_featured"]) ,
            models.Index(fields = ["category", "is_best_seller"]) ,
            models.Index(fields = ["brand","status"]) ,
            models.Index (fields = ["-purchase_count"]) ,

            models.Index(fields = ["-rating_count"]) ,
        ] 

    def __str__(self):
        return self.name 
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug      = base_slug
            counter   = 1
            # Keep trying until we find a unique slug
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.sku:
            import random, string
            # "SKU-AB3XY7KP" format
            self.sku = "SKU-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
 
        if self.original_price and self.original_price > self.price:
            self.discount_percentage = round(
                ((self.original_price - self.price) / self.original_price) * 100,
                2  # Round to 2 decimal places
            )
 
        
        
        self._build_search_text()
 
        super().save(*args, **kwargs) 
    def _build_search_text(self):
        parts = [self.name] 
        
        if self.brand:
            parts.append(f"Brand: {self.brand.name}")
        if self.category:
            
            parts.append(f"Category: {self.category.full_path}")
        if self.short_description:
            parts.append(self.short_description)
        if self.description:
           
            parts.append(self.description[:500])
        if self.tags:
            parts.append("Tags: " + ", ".join(self.tags))
        if self.specifications:
            spec_text = ", ".join(f"{k}: {v}" for k, v in self.specifications.items())
            parts.append("Specifications: " + spec_text)
        if self.features:
            parts.append("Features: " + ", ".join(self.features[:10]))
 
     
        self.search_text = "\n".join(parts) 


    @property
    def in_stock(self):
        """True if product has stock available."""
        return self.stock_quantity > 0
 
    @property
    def discount_amount(self):
        """Savings in currency (original_price - current_price)."""
        if self.original_price:
            return self.original_price - self.price
        return 0
 
 

            
class ProductImage(models.Model):
    id  = models.UUIDField(primary_key=True,default=uuid.uuid4, editable = False) 
    Product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="image") 

    image = models.ImageField(upload_to="products/images") 

    alt_text = models.CharField(max_length=200,blank=True)
    is_primary = models.BooleanField(default=False) 
    order = models.PositiveBigIntegerField(default=0)
    
    class Meta:
        db_table = "product_image" 
        ordering = ["order"] 

    def __str__ (self):
        return f"{self.product.name} - Image {self.order}" 
    

class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants") 
    name = models.CharField(max_length=255) 
    price_modifier =     models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]) 
    stock_quantity = models.PositiveIntegerField(default=0) 
    sku = models.CharField(max_length=100, unique=True) 
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "product_variants" 
       

    def __str__(self):
        return f"{self.product.name} - {self.name}" 
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews") 
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reviews") 
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]) 
    title = models.CharField(max_length=255, blank=True, null=True) 
    comment = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = "product_reviews" 
        unique_together = ["product", "user"]
        ordering = ["-created_at"] 

    def __str__(self):
        return f"{self.product.name} - {self.rating} Stars" 
    


class ProductEmbedding(models.Model):
    # Unique ID for embedding record
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # One embedding per product
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="embedding"
    )

    # AI vector used for semantic search
    embedding = VectorField(dimensions=1536)

    # Embedding model name
    model_name = models.CharField(max_length=100)

    # Hash of text used to generate embedding
    # Used to detect changes
    text_hash = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_embeddings"
        verbose_name = "Product Embedding"
        verbose_name_plural = "Product Embeddings"

    def __str__(self):
        return f"Embedding for {self.product.name}"