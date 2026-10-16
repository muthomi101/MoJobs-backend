from rest_framework import generics, permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from .models import User, FundiProfile, ClientProfile
from .serializers import UserSerializer, FundiProfileSerializer, SellerProfileSerializer

# --------------------------
# User Registration / Login
# --------------------------
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(request, phone_number=phone, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)

# --------------------------
# Fundi CRUD
# --------------------------
class FundiProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)

        profile = request.user.fundi_profile
        serializer = FundiProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)

        profile = request.user.fundi_profile
        serializer = FundiProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class FundiDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        if request.user.role != 'fundi':
            return Response({"error": "Not authorized"}, status=403)
        request.user.delete()
        return Response({"message": "Account deleted"}, status=204)

# --------------------------
# Seller CRUD
# --------------------------
class SellerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'seller':
            return Response({"error": "Not a seller"}, status=403)
        profile = request.user.seller_profile
        serializer = SellerProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        if request.user.role != 'seller':
            return Response({"error": "Not a seller"}, status=403)
        profile = request.user.seller_profile
        serializer = SellerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class SellerDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        if request.user.role != 'seller':
            return Response({"error": "Not a seller"}, status=403)
        request.user.delete()
        return Response({"message": "Seller account deleted"}, status=204)

# --------------------------
# Client CRUD
# --------------------------
class ClientRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class ClientLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = User.objects.filter(phone_number=phone_number, role='client').first()
        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Invalid credentials"}, status=401)

class ClientListView(generics.ListAPIView):
    queryset = User.objects.filter(role='client')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class ClientMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# --------------------------
# Reset Passwords
# --------------------------
class FundiResetPasswordView(APIView):
    def post(self, request):
        phone = request.data.get("phone_number")
        id_number = request.data.get("id_number")
        new_password = request.data.get("new_password")
        if not (phone and id_number and new_password):
            return Response({"error": "All fields are required"}, status=400)
        try:
            user = User.objects.get(phone_number=phone, id_number=id_number, role='fundi')
            user.password = make_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "Invalid phone number or ID number"}, status=400)

class ClientResetPasswordView(APIView):
    def post(self, request):
        phone = request.data.get("phone_number")
        id_number = request.data.get("id_number")
        new_password = request.data.get("new_password")
        if not (phone and id_number and new_password):
            return Response({"error": "All fields are required"}, status=400)
        try:
            user = User.objects.get(phone_number=phone, id_number=id_number, role='client')
            user.password = make_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "Invalid phone number or ID number"}, status=400)

# --------------------------
# Public Fundi list/detail
# --------------------------
class FundiPublicList(APIView):
    def get(self, request):
        profiles = FundiProfile.objects.select_related('user').filter(user__role='fundi')
        visible_fundis = [
            p for p in profiles if p.user.is_on_trial or p.user.is_subscribed
        ]
        data = []
        for p in visible_fundis:
            data.append({
                "id": p.user.id,
                "name": p.user.name,
                "skills": p.skills,
                "location": p.location,
                "rate_note": p.rate_note,
                "is_available": p.is_available,
                "phone_number": p.user.phone_number if p.show_contact else None,
            })
        return Response(data)

class FundiPublicDetail(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk, role='fundi')
        profile = user.fundi_profile
        return Response({
            "id": user.id,
            "name": user.name,
            "skills": profile.skills,
            "location": profile.location,
            "rate_note": profile.rate_note,
            "is_available": profile.is_available,
            "phone_number": user.phone_number if profile.show_contact else None,
        })

# --------------------------
# Health Check
# --------------------------
class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"})

