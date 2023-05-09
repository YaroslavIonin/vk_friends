from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.hashers import identify_hasher, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, name, password=None, is_active=True, is_staff=False, is_admin=False):
        if not name:
            raise ValueError('Пользователь должен иметь name')

        if not password:
            raise ValueError('Пользователь должен ввести пароль')

        user = self.model(name=name)
        user.set_password(password)
        user.is_staff = is_staff
        user.is_admin = is_admin
        user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None):
        user = self.create_user(name=name, password=password, is_active=True,
                                is_staff=True, is_admin=True)
        print(user)
        return user


class User(AbstractBaseUser):
    name = models.CharField(unique=True, max_length=255, verbose_name='Никнейм')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_friends', default=[], blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False, verbose_name='Админ')

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # def __str__(self):
    #     return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        try:
            _alg_ = identify_hasher(self.password)
        except ValueError:
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']


class Bid(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_from',
                                  verbose_name='От кого:',
                                  on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_to', verbose_name='Кому:',
                                on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=[
        (0, 'Отправленная заявка'),
        (1, 'Принятая заявка'),
        (2, 'Отклонённая заявка'),

    ], default=0, verbose_name='Статус заявки')

    def save(self, *args, **kwargs):
        if self.user_to == self.user_from:
            raise Exception("Нельзя подавать заявку в друзья самому себе")

        try:
            bid = Bid.objects.get(user_from=self.user_from, user_to=self.user_to)
        except ObjectDoesNotExist:
            try:
                bid_first = Bid.objects.get(user_from=self.user_to, user_to=self.user_from)
            except ObjectDoesNotExist:
                super().save(*args, **kwargs)
            else:
                if bid_first.status == 1:
                    raise Exception("Вы уже друзья с этим пользователем")

                bid_first.status = 1
                self.status = 1

                super(Bid, bid_first).save()
                super().save(*args, **kwargs)

                user_1, user_2 = User.objects.get(id=self.user_from.id), User.objects.get(id=self.user_to.id)

                user_1.user_friends.add(user_2)
                user_2.user_friends.add(user_1)

        else:
            if bid.status == self.status == 0:
                raise Exception("Вы уже подали заявку в друзья этому пользователю")
            elif bid.status == 1:
                raise Exception("Вы уже друзья с этим пользователем")

            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['status']
