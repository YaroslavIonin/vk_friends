from rest_framework import serializers
from .models import User, Bid
from django.contrib.auth import get_user_model


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, label='Пароль ещё раз')

    class Meta:
        model = get_user_model()
        fields = [
            "name",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        name = validated_data["name"]
        password = validated_data["password"]
        password2 = validated_data["password2"]
        if password != password2:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        user = User(name=name)
        user.save()
        return user


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'


class BidPostSerializer(serializers.ModelSerializer):
    user_from = serializers.IntegerField(label='User id',
                                         help_text='Какой пользователь подаёт заявку в друзья')
    user_to = serializers.IntegerField(label='User id',
                                       help_text='Какому пользователя подаётся заявка в друзья')

    class Meta:
        model = Bid
        fields = ('user_from', 'user_to')


class BidPatchSerializer(serializers.ModelSerializer):
    status_do = serializers.IntegerField(label='Статус действия:',
                                         help_text='0 - Отклонить заявку;\n'
                                                   '1 - Принять заявку;')

    class Meta:
        model = Bid
        fields = ('status_do',)


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id',)

