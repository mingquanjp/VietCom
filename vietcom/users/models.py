from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, phone, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        if not phone:
            raise ValueError('Phone number must be provided')
        if not full_name:
            raise ValueError('Full name must be provided')
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            full_name=full_name,
            username=email,  # Use email as username
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone, full_name, password, **extra_fields)

class User(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),  
        ('other', 'Other'),
        ('not_specified', 'Not specified'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('busy', 'Busy'),
        ('away', 'Away'),
        ('available', 'Available for connection'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999' or '0999999999'"
    )
    
    email = models.EmailField(unique=True)
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        unique=True,
        help_text="Phone number must be in the format: '+84xxxxxxxxx' or '0xxxxxxxxx'"
    )
    full_name = models.CharField(max_length=100)
    hometown = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='not_specified',
        help_text="User's gender"
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short introduction about yourself (max 500 characters)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        help_text="Current status"
    )
    interests = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude")
    search_radius = models.FloatField(default=50.0, help_text="Search radius (km)")
    level = models.IntegerField(default=1)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'full_name']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_display_name(self):
        return self.full_name or self.username
    
    def get_search_radius_by_level(self):
        """Calculate search radius based on user level: 5 + (level-1) * 2"""
        return 5 + (self.level - 1) * 2
    
    def level_up(self):
        """Increase user level by 1"""
        self.level += 1
        self.save()
        return self.level
    
    def get_level_info(self):
        """Get level information including current and next level radius"""
        current_radius = self.get_search_radius_by_level()
        next_radius = 5 + self.level * 2  # Next level radius
        return {
            'current_level': self.level,
            'current_radius': current_radius,
            'next_level': self.level + 1,
            'next_radius': next_radius
        }
    
    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()
