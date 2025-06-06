from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

# Create your models here.

class CustomUserManager(UserManager):
    def _create_user(self, email: str, username: str, password: str, **extra_fields) -> 'User':
        """
        Create and save a User with the given email, username, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, username=None, password=None, **extra_fields) -> 'User':
        """
        Create and save a regular User with the given email, username, and password.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email=None, username=None, password=None, **extra_fields) -> 'User':
        """
        Create and save a SuperUser with the given email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(verbose_name="Date of Birth", null=True)

    # User Permissions/misc
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'

    def get_full_name(self) -> str:
        """
        Return the user's full name.
        """
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self) -> str:
        """
        Return the user's short name.
        """
        return self.email.split('@')[0]

    def __str__(self) -> str:
        """
        Return a string representation of the user.
        """
        return f'{self.email} - ({self.user_id})'

    def follower_count(self) -> int:
        """
        Return the number of followers for the user.
        """
        return self.followers.count()

    def following_count(self) -> int:
        """
        Return the number of users this user is following.
        """
        return self.following.count()

    def friend_count(self) -> int:
        """
        Return the number of friends for the user.
        """
        return self.friends.count()

class Workout(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.category})"

class Overload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Overload Date', auto_now_add=True)
    workouts = models.ManyToManyField(Workout, through="WorkoutEntry")  # Using an intermediary table

    def __str__(self):
        return f"Overload for {self.user.username} on {self.date}"


class WorkoutEntry(models.Model):
    """Intermediate table to track reps for workouts inside an Overload."""
    overload = models.ForeignKey(Overload, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    reps = models.PositiveIntegerField(default=0)  # Tracking reps per workout

    def __str__(self):
        return f"{self.workout.name}: {self.reps} reps ({self.overload.user.username})"
