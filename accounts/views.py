from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            name = form.cleaned_data['name'].strip()
            password = form.cleaned_data['password']

            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered.")
                return redirect('signup')

            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            login(request, user)
            request.session['show_age_modal'] = True
            return redirect('home')
        else:
            # handle specific error messages (prompt requirements)
            if form.errors.get('email'):
                messages.error(request, "Please enter a valid email address.")
            if form.errors.get('password'):
                messages.error(request, "Password must be at least 6 characters.")
            if form.errors.get('age_confirm'):
                messages.error(request, "You must confirm that you are 18 or older to sign up.")
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                request.session['show_age_modal'] = True
                return redirect('home')
            messages.error(request, "Incorrect email or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
