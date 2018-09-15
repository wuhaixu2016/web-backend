from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from .models import New, Video
from .forms import NameForm
from .object.test_ssd_mobilenet import *
from django.contrib import auth
from django import forms
from django.contrib.auth.models import User
import threading
from django.utils import timezone
from django.contrib import messages

left = 0
right = 200
top = 0
bottom = 200

def index(request):
    if get_status() == 0:
        change_status()
        time.sleep(1)
    is_def = 0
    for key in request.session.keys():
        if(key == 'username'):
            is_def = 1
    if(is_def == 0):
        request.session['username'] = 0

    if(request.session['username'] == 1):
        message = ""
        if(request.method == 'POST'):
            try:
                m = request.POST['video_url']

                news_list = Video.objects.filter(video_url= m)
                if len(news_list) != 0:
                    message = "视频已经存在"
                else:
                    n = Video(video_title = m, video_date = timezone.now(), video_url = m)
                    n.save()
            except :
                pass
        video_list = Video.objects.order_by('-video_date')
        return render(request, 'news/index.html',{'message': message, "video_list": video_list})
    else:
        return HttpResponseRedirect(reverse('login'))
    return HttpResponseRedirect(reverse('login'))

def login(request):
    if get_status() == 0:
        change_status()
        time.sleep(1)
    is_def = 0
    for key in request.session.keys():
        if(key == 'username'):
            is_def = 1
    if(is_def == 0):
        request.session['username'] = 0

    if(request.session['username'] == 1):
        message = ""
        video_list = Video.objects.order_by('-video_date')
        template = loader.get_template('news/index.html')
        context = {'message': message, "video_list": video_list}
        return HttpResponseRedirect(reverse('index'))

    if(request.method == 'POST'):
        m_UserForm = NameForm(request.POST)
        if(m_UserForm.is_valid()):
            username = request.POST['username']
            password = request.POST['password']

            if(username == 'admin' and password == '123456'):
                request.session['super'] = 1
                request.session['username'] = 1
                return HttpResponseRedirect(reverse('register'))

            user = auth.authenticate(username = username, password = password)

            if(user):
                request.session['super'] = 0
                request.session['username'] = 1
                message = ""
                video_list = Video.objects.order_by('-video_date')
                template = loader.get_template('news/index.html')
                context = {'message': message, "video_list": video_list}
                return HttpResponseRedirect(reverse('index'))

            else:
                messages.add_message(request, messages.INFO, '用户名或密码错误')
                request.session['super'] = 0
                request.session['username'] = 0
                return render(request, 'news/login.html')
        return render(request, 'news/login.html')
    return render(request, 'news/login.html')

def register(request):
    is_def = 0
    for key in request.session.keys():
        if(key == 'super'):
            is_def = 1
    if(is_def == 0):
        request.session['super'] = 0

    t = request.session['super']
    if(t == 1):
        if(request.method == 'POST'):
            m_UserForm = NameForm(request.POST)
            if(m_UserForm.is_valid()):
                username = request.POST['username']
                password = request.POST['password']
                password2 = request.POST['password2']
                if(password != password2):
                    messages.add_message(request, messages.INFO, '请确认密码')
                    return render(request, 'news/register.html')
                
                result = User.objects.filter(username = username)
                if(result):
                    messages.add_message(request, messages.INFO, '用户已存在')
                    return render(request, 'news/register.html')

                user = User.objects.create_user(username = username, password = password)
                user.save()
                auth.login(request, user)
                request.session['super'] = 0
                messages.add_message(request, messages.INFO, '注册成功')
                return HttpResponseRedirect(reverse('login'))
        return render(request, 'news/register.html')
    else:
        return HttpResponseRedirect(reverse('login'))

def logout(request):
    if get_status() == 0:
        change_status()
        time.sleep(1)
    request.session['username'] = 0
    request.session['super'] = 0
    messages.add_message(request, messages.INFO, '已退出登陆')
    return HttpResponseRedirect(reverse('login'))

def change(request):
    if get_status() == 0:
        change_status()
        time.sleep(1)
    if(request.method == 'POST'):
        m_UserForm = NameForm(request.POST)
        if(m_UserForm.is_valid()):
            username = request.POST['username']
            password = request.POST['password']
            password2 = request.POST['password2']
            password3 = request.POST['password3']

            result = User.objects.filter(username = username)
            if(result == None or username == 'admin'):
                #不能修改密码，错误提示
                messages.add_message(request, messages.INFO, '用户名或密码错误')
                return HttpResponseRedirect(reverse('login'))

            if(password3 != password2):
                    messages.add_message(request, messages.INFO, '请确认密码')
                    return render(request, 'news/change.html')

            user = auth.authenticate(username = username, password = password)
            if(user):#已有用户
                User.objects.filter(username = username).delete()
                user = User.objects.create_user(username = username, password = password2)
                user.save()
                auth.login(request, user)
                request.session['super'] = 0
                request.session['username'] = 0
                messages.add_message(request, messages.INFO, '修改密码成功')
                return HttpResponseRedirect(reverse('login'))
            else:
                messages.add_message(request, messages.INFO, '用户名或密码错误')
                return render(request, 'news/change.html')
    return render(request, 'news/change.html')

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)
    def get_result(self):
        try:
            return self.result
        except :
            pass

def test(v_id):
    p = model()
    return StreamingHttpResponse(p.work(v_id, 0), content_type="multipart/x-mixed-replace; boundary=frame")

def video(request, video_id):
    if get_status() == 1:
        change_status()
        time.sleep(1)
    video_id = int(video_id)
    v = get_object_or_404(Video, pk=video_id)
    v_id = str(v.video_url)
    if(v_id == '0'):
        v_id = 0
    t = MyThread(test, (v_id,), str(video_id))
    t.start()
    return t.get_result()

# deal with detail
def show(request, video_id):
    global left, right, top, bottom, show_id
    if(request.method == 'POST'):
        try:
            if(request.POST['left'].isdigit() and request.POST['right'].isdigit() and request.POST['top'].isdigit() and request.POST['bottom'].isdigit()):
                left = int(request.POST['left'])
                right = int(request.POST['right'])
                top = int(request.POST['top'])
                bottom = int(request.POST['bottom'])
        except :
            pass
    if get_status() == 0:
        change_status()
        time.sleep(1)
    is_def = 0
    for key in request.session.keys():
        if(key == 'username'):
            is_def = 1
    if(is_def == 0):
        request.session['username'] = 0

    if(request.session['username'] == 1):
        show_id = get_channel()
        return render(request, 'news/show.html',{"video_id":video_id, "track": show_id, "left": left, "right":right, "top":top, "bottom":bottom})
    else:
        return HttpResponseRedirect(reverse('login'))

# deal with alarm cal
def alarm_meta(v_id, video_id, left = 0, right = 500, top = 0, bottom = 500):
    p = model()
    return StreamingHttpResponse(p.work(v_id, 1, video_id, left, right, top, bottom), content_type="multipart/x-mixed-replace; boundary=frame")

def alarm(request, video_id):
    global left, right, top, bottom
    if get_status() == 1:
        change_status()
        time.sleep(1)
    video_id = int(video_id)
    v = get_object_or_404(Video, pk=video_id)
    v_id = str(v.video_url)
    if(v_id == '0'):
        v_id = 0
    t = MyThread(alarm_meta, (v_id, video_id, left,right,top,bottom,), str(video_id))
    t.start()
    return t.get_result()

# showAlarm
def showAlarm(request, video_id):
    is_def = 0
    for key in request.session.keys():
        if(key == 'username'):
            is_def = 1
    if(is_def == 0):
        request.session['username'] = 0

    if(request.session['username'] == 1):
        news_list = New.objects.filter(news_type=video_id)
        return render(request, 'news/alarm.html',{"news_list": news_list, "video_id": video_id})

# deleteAlarm
def delete(request, alarm_id, video_id):
    n = New.objects.get(pk=alarm_id)
    m = n.news_type
    n.delete()
    news_list = New.objects.filter(news_type=m)
    return render(request, 'news/alarm.html',{"news_list": news_list, "video_id": video_id})

# deleteAlarm
def deleteall(request, video_id):
    is_def = 0
    for key in request.session.keys():
        if(key == 'username'):
            is_def = 1
    if(is_def == 0):
        request.session['username'] = 0

    if(request.session['username'] == 1):
        news_list = New.objects.filter(news_type=video_id)
        for i in range(len(news_list)):
            news_list[i].delete()
    news_list = New.objects.filter(news_type=video_id)
    return render(request, 'news/alarm.html',{"news_list": news_list, "video_id": video_id})

# change to another view
def changeChannel(request, video_id):
    change_channel()
    show_id = get_channel()
    global left, right, top, bottom
    return render(request, 'news/show.html',{"video_id":video_id, "track": show_id, "left": left, "right":right, "top":top, "bottom":bottom})