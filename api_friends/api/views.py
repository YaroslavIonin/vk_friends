import json
from http.client import HTTPResponse

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.viewsets import ModelViewSet

from api.models import Bid, User
from django.db.models import Q
from api.serializers import RegisterSerializer, BidSerializer, FriendsSerializer, BidPostSerializer, BidPatchSerializer


class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description='Возвращает созданного пользователя либо возникшую ошибку',
        operation_summary='Регистрация пользователя',

    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Пользователь успешно создан",
        })


class BidView(ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

    @swagger_auto_schema(
        operation_summary='Исходящие / Входящие заявки',
        operation_description='Возвращает список исходящих или '
                              'входящих заявок в зависимости от '
                              'значения status_to_or_in',
        manual_parameters=[
            openapi.Parameter(
                'user',
                openapi.IN_QUERY,
                type='int',
                description='ID пользователя, от кого запрос'
            ),
            openapi.Parameter(
                'status_to_or_in',
                openapi.IN_QUERY,
                type='int',
                description='Посмотреть входящие заявки - 1\n'
                            'Посмотреть исходящие заявки - 0'
            ),
        ]

    )
    def list(self, request, *args, **kwargs):
        data = self.request.query_params
        if 'status_to_or_in' in data and 'user' in data:
            if data.get('status_to_or_in') == '0':
                bids = Bid.objects.filter(Q(user_from=data.get('user')) & (Q(status=0) | Q(status=2)))
            elif data.get('status_to_or_in') == '1':
                bids = Bid.objects.filter(Q(user_to=data.get('user')) & (Q(status=0) | Q(status=2)))
            else:
                return Response({
                    "error": 'Некорректное значение status_to_or_in'
                })
            return Response({
                "bids": BidSerializer(bids, many=True).data
            })
        else:
            return Response({
                "error": 'Запрос должен содержать status_to_or_in и user'
            })

    @swagger_auto_schema(
        operation_summary='Создание заявки в друзья',
        operation_description='Возвращает созданную заявку в друзья либо возникшую ошибку',
        request_body=BidPostSerializer
    )
    def create(self, request, *args, **kwargs):
        try:
            bid = super(BidView, self).create(request, *args, **kwargs)
        except Exception as exception:
            return Response({
                "error": exception.args[0]
            })
        return bid

    @swagger_auto_schema(
        operation_summary='Принятие / отклонение заявки в друзья',
        operation_description='Возвращает результат принятия / отклонения заявки в друзья либо возникшую ошибку',
        request_body=BidPatchSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                type='integer',
                description='ID заявки'
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        if 'status_do' in request.data:
            status_do = request.data.get('status_do')
            if status_do == 0:
                status = 2
                message = 'Заявка отклонена'
            elif status_do == 1:
                status = 1
                message = 'Заявка принята'
            else:
                return Response({
                    'error': 'status_do может быть либо 0 (отклонить заявку), '
                             'либо 1 (принять заявку)'
                })

            obj = self.get_object()
            obj.status = status

            user_1, user_2 = User.objects.get(id=obj.user_from.id), User.objects.get(id=obj.user_to.id)

            user_1.user_friends.add(user_2)
            user_2.user_friends.add(user_1)

            try:
                obj.save()
            except Exception as exception:
                return Response({
                    "error": exception.args[0]
                })
            return Response({
                'message': message
            })

        return Response({
            'error': 'Запрос должен принимать id заявки и '
                     'status_do со значением 0 - отклонить заявку, либо 1 - принять заявку'
        })

    @swagger_auto_schema(
        operation_summary='Статус дружбы',
        operation_description='Возвращает статус дружбы с пользоватетелем',
        manual_parameters=[
            openapi.Parameter(
                'user_from',
                openapi.IN_QUERY,
                type='integer',
                description='ID пользователя'
            ),
            openapi.Parameter(
                'user_to',
                openapi.IN_QUERY,
                type='integer',
                description='ID пользователя, с которым проверяется статус дружбы'
            ),
        ],
    )
    def check_status(self, request):
        data = self.request.query_params
        if 'user_from' in data and 'user_to' in data:
            user_from = request.GET.get('user_from')
            user_to = request.GET.get('user_to')
            try:
                bid = self.queryset.get(user_from=user_from, user_to=user_to)
            except ObjectDoesNotExist:
                try:
                    bid_1 = self.queryset.get(user_from=user_to, user_to=user_from)
                except ObjectDoesNotExist:
                    message = 'Нет исходящих и входящих заявок'
                else:
                    if bid_1.status == 1:
                        message = 'Уже друзья'
                    else:
                        message = 'Есть входящая заявка'
            else:
                if bid.status == 1:
                    message = 'Уже друзья'
                else:
                    message = 'Есть исходящая заявка'
        else:
            return Response({
                'error': 'Запрос должен принимать user_from (от кого) '
                         'и user_to (с каким пользователем проверяется состояние дружбы)'
            })

        return Response({
            'status': message
        })


class FriendsView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FriendsSerializer

    @swagger_auto_schema(
        operation_summary='Получить друзей',
        operation_description='Возвращает список друзей пользователя',
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                type='integer',
                description='ID пользователя, от кого запрос'
            ),
        ]

    )
    def list(self, request, *args, **kwargs):
        data = self.request.query_params
        if 'user_id' in data:
            try:
                user = User.objects.get(id=data.get('user_id'))
            except ObjectDoesNotExist:
                return Response({
                    'error': "Пользователя с таким user_id не существует"
                })
            print(user.friends.all())
            result = {"friends": []}
            for friend in user.friends.all():
                result['friends'].append({
                    'id': friend.id,
                    'name': friend.name
                })
            return Response(result)
        return Response({
            'error': "Запрос должен содержать user_id - чьих друзей вывести"
        })

    @swagger_auto_schema(
        operation_summary='Удаление пользователя из друзей',
        operation_description='Возвращает результат удаления пользователя из друзей либо возникшую ошибку',
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                type='integer',
                description='ID пользователя'
            ),
            openapi.Parameter(
                'del_user',
                openapi.IN_QUERY,
                required=True,
                type='integer',
                description='ID пользователя, которого нужно удалить'
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        data = self.request.query_params
        if 'del_user' in data:
            user = self.get_object()
            del_user = User.objects.get(id=data.get('del_user'))
            if del_user in user.friends.all():
                user.friends.remove(del_user)
                del_user.friends.remove(user)
                try:
                    bid_1 = Bid.objects.get(user_from=user.id, user_to=del_user.id)
                except ObjectDoesNotExist:
                    bid_2 = Bid.objects.get(user_from=del_user.id, user_to=user.id)
                    bid_2.status = 0
                    super(Bid, bid_2).save()
                else:
                    try:
                        bid_2 = Bid.objects.get(user_from=del_user.id, user_to=user.id)
                    except ObjectDoesNotExist:
                        bid_1.user_from, bid_1.user_to = bid_1.user_to, bid_1.user_from
                        bid_1.status = 0
                        super(Bid, bid_1).save()
                    else:
                        bid_1.delete()
                        bid_2.status = 0
                        super(Bid, bid_2).save()

                return Response({
                    'message': 'Пользователь удалён из ваших друзей'
                })
            else:
                return Response({
                    'error': 'Такого пользователя нет в ваших друзьях'
                })
        else:
            return Response({
                'error': 'Запрос должен содержать del_user (id удаляемого пользователся)'
            })


