from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Попробовать взять токен из cookie
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            # Если токена в cookie нет, то использовать стандартный метод (из заголовков)
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token