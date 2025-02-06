from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # 创建用户但不立即保存
            user = form.save(commit=False)
            # 获取并设置邮箱
            email = request.POST.get('email')
            if email:
                user.email = email
                user.save()
                # 登录用户
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('home')
            else:
                messages.error(request, 'Email is required!')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

