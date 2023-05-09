from django.contrib import admin
from .models import User, Bid


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    fields = ('name', 'friends')
    empty_value_display = '-empty-'
    list_filter = ('name',)
    search_fields = ['name']
    search_help_text = 'Поиск осуществляется по никнейму пользователей'


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_from', 'user_to', 'status']
    fields = (('user_from', 'user_to'), 'status')
    empty_value_display = '-empty-'
