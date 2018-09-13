from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from .models import New
from .forms import NameForm
from .object.test_ssd_mobilenet import *
from django.contrib import auth
from django import forms
from django.contrib.auth.models import User


def index(request):
    is_def = 0
    for key in request.session.keys():
        if(key == 'username'):
            is_def = 1
    if(is_def == 0):
        request.session['username'] = 0

    if(request.session['username'] == 1):
        news_list = New.objects.order_by('-news_date')
        template = loader.get_template('news/index.html')
        context = {
            'news_list': news_list,
        }
        return HttpResponse(template.render(context, request))
    else:
        return render(request, 'news/login.html')
    return render(request, 'news/login.html')

def login(request):
    if(request.session['username'] == 1):
        news_list = New.objects.order_by('-news_date')
        template = loader.get_template('news/index.html')
        context = {
            'news_list': news_list,
        }
        return render(request, 'news/index.html')

    if(request.method == 'POST'):
        m_UserForm = NameForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']

        if(username == 'admin' and password == '123456'):
            request.session['super'] = 1
            request.session['username'] = 1
            return render(request, 'news/register.html')

        user = auth.authenticate(username = username, password = password)

        if(user):
            request.session['super'] = 0
            request.session['username'] = 1
            return render(request, 'news/index.html')

        else:
            request.session['super'] = 0
            request.session['username'] = 0
            return render(request, 'news/login.html')
            
    return render(request, 'news/login.html')

def register(request):
    t = request.session['super']
    if(t == 1):
        if(request.method == 'POST'):
            m_UserForm = NameForm(request.POST)
            if(m_UserForm.is_valid()):
                username = request.POST['username']
                password = request.POST['password']
                password2 = request.POST['password2']
                if(password != password2):
                    return render(request, 'news/register.html')
                
                result = User.objects.filter(username = username)
                if(result):
                    return render(request, 'news/register.html')

                user = auth.authenticate(username = username, password = password)
                print(user)

                if(user):#已有用户
                    return render(request, 'news/register.html')

                user = User.objects.create_user(username = username, password = password)
                user.save()
                auth.login(request, user)
                request.session['super'] = 0
                return render(request, 'news/login.html')
    else:
        return render(request, 'news/login.html')

def logout(request):
    print('1\n\n')
    request.session['username'] = 0
    request.session['super'] = 0
    return HttpResponseRedirect(reverse('login'))

def change(request):
    if(request.method == 'POST'):
        m_UserForm = NameForm(request.POST)
        if(m_UserForm.is_valid()):
            username = request.POST['username']
            password = request.POST['password']
            password2 = request.POST['password2']

            result = User.objects.filter(username = username)
            if(result == None or username == 'admin'):
                #不能修改密码，错误提示
                return render(request, 'news/logout.html')

            user = auth.authenticate(username = username, password = password)
            print(user)
            if(user):#已有用户
                User.objects.filter(username = username).delete()
                user = User.objects.create_user(username = username, password = password2)
                user.save()
                auth.login(request, user)
                request.session['super'] = 0
                request.session['username'] = 0
                return render(request, 'news/login.html')
            else:
                return render(request, 'news/logout.html')
    return render(request, 'news/change.html')

def video(request):
    p = model()
    return StreamingHttpResponse(p.work(), content_type="multipart/x-mixed-replace; boundary=frame")

def show(request):
    return render(request, 'news/show.html')