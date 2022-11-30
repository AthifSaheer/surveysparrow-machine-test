from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import URL
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
        c_password = request.POST.get('c_password')

        if not name or not password:
            return render(request, 'register.html', {'error': 'Username & password are required!'})

        if password != c_password:
            return render(request, 'register.html', {'error': 'Password did not match!'})

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
        
        all_urls = URL.objects.filter(user=request.user).order_by('-id')
        active_urls = URL.objects.filter(user=request.user, active=True).order_by('-id')
        deleted_urls = URL.objects.filter(user=request.user, active=False).order_by('-id')

        context = {
            'urls': all_urls if all_urls else 'nodata',
            'active_urls': active_urls if active_urls else 'nodata',
            'deleted_urls': deleted_urls if deleted_urls else 'nodata',
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
        error_msg = ''
        code = 0
        new_url = ''

        if "https://" not in url.url:
            new_url = f"https://www.{url.url}/"

        try:
            if new_url == '':
                code = urllib.request.urlopen(url.url).getcode()
            else:
                code = urllib.request.urlopen(new_url).getcode()
        except urllib.error.HTTPError:
            error_msg = "Return 403: Forbidden!"
        except urllib.error.URLError:
            error_msg = "URL or service not known"
        else:
            error_msg = "Something went wrong!"

        data = {}
        if code == 200:
            data["server"] = "up"
        elif error_msg != '':
            data["error"] = error_msg
        else:
            data["server"] = "down"

        return JsonResponse(data)
