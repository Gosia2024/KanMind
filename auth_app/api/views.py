from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import LoginSerializer, RegistrationSerializer

User = get_user_model()

class RegistrationView(APIView):
    """
    POST /api/registration/
    Creates a new user and returns an auth token + basic user info.
    Permissions: AllowAny
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        return Response(
            {
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )

class LoginView(APIView):
    """
    POST /api/login/
    Authenticates user by email/password and returns an auth token + user info.
    Permissions: AllowAny
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()

        return Response(
            {
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )

class EmailCheckView(APIView):
    """
    GET /api/email-check/?email=...
    Checks if a user with a given email exists and returns basic user info.
    Permissions: IsAuthenticated
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {"id": user.id, "email": user.email, "fullname": user.fullname},
            status=status.HTTP_200_OK,
        )
