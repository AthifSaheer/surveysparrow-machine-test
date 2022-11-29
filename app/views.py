from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import URL
from django.http import JsonResponse
import urllib.request

def register(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return render(request, 'register.html')
        else:
            return redirect('home')
         
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        if not name or not password:
            return render(request, 'register.html', {'error': 'Username & password are required!'})

        if User.objects.filter(username=name):
            return render(request, 'register.html', {'error': 'User already exists!'})

        User.objects.create_user(username=name, password=password)
        return redirect('login')
    
def login(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return render(request, 'login.html')
        else:
            return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials!'})

def logout(request):
    auth_logout(request)
    return redirect('login')

def home(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('login')
        
        urls = URL.objects.filter(user=request.user, active=True)
        context = {
            'urls': urls if urls else 'nodata'
        }
        return render(request, 'home.html', context)

def add_new_url(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('login')
        
        return render(request, 'add_new_url.html')
        
    if request.method == 'POST':
        url = request.POST.get('url')
        interval = request.POST.get('interval')

        url_obj = URL()
        url_obj.user = request.user
        url_obj.url = url
        url_obj.interval = interval
        url_obj.active = True
        url_obj.save()
        return redirect("home")

def edit_url(request, url_id):
    if request.method == 'GET':
        url = URL.objects.get(id=url_id)
        return render(request, 'edit_url.html', {'url': url})

    if request.method == 'POST':
        url = request.POST.get('url')
        interval = request.POST.get('interval')

        url_obj = URL.objects.get(id=url_id)
        url_obj.url = url
        url_obj.interval = interval
        url_obj.save()
        return redirect("home")

def delete_url(request, url_id):
    if request.method == 'GET':
        url = URL.objects.get(id=url_id)
        url.active = False
        url.save()
        return redirect('home')

def monitor_url(request, url_id):
    if request.method == 'GET':
        url = URL.objects.get(id=url_id)
        return render(request, 'monitor_url.html', {'url': url})
        
    if request.method == 'POST':
        url = URL.objects.get(id=url_id)
        try:
            code = urllib.request.urlopen(url.url).getcode()
        except:
            code = 0

        data = {}
        if code == 200:
            data["server"] = "up"
        elif code == 0:
            data["error"] = "Invalid url"
        else:
            data["server"] = "down"
        return JsonResponse(data)
