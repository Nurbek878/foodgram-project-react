from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from .serializers import NewUserSerializer
from user.models import NewUser

class NewUserViewset(UserViewSet):
    queryset = NewUser.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = NewUserSerializer