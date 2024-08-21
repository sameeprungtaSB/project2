from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Member
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
import base64
import secrets

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)

        try:
            user = User(
                email=email,
                username=username,
                phone_number=phone_number,
                password=make_password(password)
            )
            user.clean()  # Validate unique email
            user.save()
            return JsonResponse({'redirect': '/login/'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'registration/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            request.session['username'] = user.username
            return JsonResponse({'redirect': '/home/'})
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return render(request, 'registration/login.html')

def home(request):
    username = request.session.get('username', 'Guest')
    return render(request, 'registration/home.html', {'username': username})

def crud_operations(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            profile_picture = request.FILES.get('profile_picture')
            password = secrets.token_urlsafe(8)

            profile_picture_base64 = None
            if profile_picture:
                image = Image.open(profile_picture)
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                profile_picture_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            Member.create(
                name=name,
                email=email,
                phone_number=phone_number,
                password=make_password(password),
                profile_picture=profile_picture_base64
            )
            return redirect('crud_operations')

        elif action == 'delete':
            email = request.POST.get('email')
            if email:
                Member.objects.filter(email=email).delete()
            return redirect('crud_operations')

        elif action == 'update':
            old_email = request.POST.get('old_email')
            name = request.POST.get('name')
            phone_number = request.POST.get('phone_number')
            new_password = request.POST.get('password')
            profile_picture = request.FILES.get('profile_picture')

            try:
                member = Member.objects.get(email=old_email)
                if old_email != request.POST.get('email'):
                    new_email = request.POST.get('email')
                    new_member = Member(
                        email=new_email,
                        name=name or member.name,
                        phone_number=phone_number or member.phone_number,
                        profile_picture=None
                    )
                    if profile_picture:
                        image = Image.open(profile_picture)
                        buffered = BytesIO()
                        image.save(buffered, format="JPEG")
                        new_member.profile_picture = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    else:
                        new_member.profile_picture = member.profile_picture
                    new_member.save()
                    Member.objects.filter(email=old_email).delete()
                else:
                    if name:
                        member.name = name
                    if phone_number:
                        member.phone_number = phone_number
                    if new_password:
                        member.password = make_password(new_password)
                    if profile_picture:
                        image = Image.open(profile_picture)
                        buffered = BytesIO()
                        image.save(buffered, format="JPEG")
                        member.profile_picture = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    member.save()
                return redirect('crud_operations')
            except Member.DoesNotExist:
                return JsonResponse({'error': 'Member not found.'}, status=404)

    members = Member.objects.all()
    return render(request, 'registration/crud_operations.html', {'members': members})

@csrf_exempt
def create_member(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        profile_picture = request.FILES.get('profile_picture')
        password = secrets.token_urlsafe(8)

        profile_picture_base64 = None
        if profile_picture:
            image = Image.open(profile_picture)
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            profile_picture_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        Member.create(
            name=name,
            email=email,
            phone_number=phone_number,
            password=make_password(password),
            profile_picture=profile_picture_base64
        )
        return redirect('crud_operations')

    return render(request, 'registration/create_member.html')

@csrf_exempt
def view_members(request):
    members = Member.objects.all()
    return render(request, 'registration/view_members.html', {'members': members})

@csrf_exempt
def update_member(request):
    if request.method == 'POST':
        old_email = request.POST.get('old_email')
        new_email = request.POST.get('email')
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        profile_picture = request.FILES.get('profile_picture')

        try:
            if old_email != new_email:
                old_member = Member.objects.get(email=old_email)
                new_member = Member(
                    email=new_email,
                    name=name or old_member.name,
                    phone_number=phone_number or old_member.phone_number
                )
                if profile_picture:
                    image = Image.open(profile_picture)
                    buffered = BytesIO()
                    image.save(buffered, format="JPEG")
                    new_member.profile_picture = base64.b64encode(buffered.getvalue()).decode('utf-8')
                else:
                    new_member.profile_picture = old_member.profile_picture
                new_member.save()
                Member.objects.filter(email=old_email).delete()
            else:
                member = Member.objects.get(email=old_email)
                if name:
                    member.name = name
                if phone_number:
                    member.phone_number = phone_number
                if profile_picture:
                    image = Image.open(profile_picture)
                    buffered = BytesIO()
                    image.save(buffered, format="JPEG")
                    member.profile_picture = base64.b64encode(buffered.getvalue()).decode('utf-8')
                member.save()

            return redirect('crud_operations')
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'}, status=404)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def delete_member(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            member = Member.objects.get(email=email)
            member.delete()
            return redirect('crud_operations')
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'}, status=404)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
