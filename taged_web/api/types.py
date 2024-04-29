from typing import cast

from rest_framework.generics import GenericAPIView

from taged_web.models import User


class UserGenericAPIView(GenericAPIView):

    def current_user(self) -> User:
        return cast(User, self.request.user)
