import uuid 
from django.db import models 
from django.utils import timezone 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin): 
    class Roles(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True) 
    username = models.CharField(max_length=150, blank=True, null=True) 
    first_name = models.CharField(max_length=30, blank=True) 
    last_name = models.CharField(max_length=30, blank=True)  
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True) 
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CUSTOMER)
    is_active = models.BooleanField(default=True)    
    is_staff = models.BooleanField(default=False) 
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now) 
    last_login = models.DateTimeField(blank=True, null=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    prefrences = models.JSONField(blank=True, null=True) 
    browsing_history = models.JSONField(blank=True, null=True) 
    objects = UserManager() 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'   
        db_table = 'users' 
        ordering = ['-date_joined'] 

    def __str__(self):
        return f"{self.full_name} <{self.email}>" 
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() 
    def is_admin(self):
        return self.role == self.Roles.ADMIN     
    
    def add_to_browsing_history(self, product_id: str, max_history: int = 50):
        """Add product to browsing history, keeping only the most recent entries."""
        history = self.browsing_history or []
        # Remove if already exists to move to front
        product_id = str(product_id)
        if product_id in history:
            history.remove(product_id)
        history.insert(0, product_id)
        self.browsing_history = history[:max_history]
        self.save(update_fields=["browsing_history"]) 


class Address(models.Model):
    class AddressType(models.TextChoices):
        SHIPPING = 'SHIPPING', 'Shipping'
        BILLING = 'BILLING', 'Billing'  
        BOTH = 'BOTH', 'Both' 
    id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE) 
    label = models.CharField(max_length=100, default='Home') 
    adress_type = models.CharField(max_length=20, choices=AddressType.choices, default=AddressType.BOTH) 
    full_name = models.CharField(max_length=100) 
    phone_number = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100) 
    postal_code = models.CharField(max_length=20) 
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses' 
        db_table = 'addresses' 
        ordering = ['-created_at'] 
    def __str__(self):
        return f"{self.full_name} - {self.address_line1}, {self.city}" 
    def save(self, *args, **kwargs):
        if self.is_default:
            # Unset default for other addresses of the same user
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs) 

