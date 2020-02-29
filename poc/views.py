from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django import forms
import os
import magic
import tempfile
# Create your views here.

@login_required(login_url='login')
def index(request):
    username = request.session['username']
    return render(request, 'index.html', { 'username' : username })

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = authenticate(username=username,password=password)
        if user is not None:
            print("user found")
            if user.is_active:
                request.session.set_expiry(86400)
                login(request,user)
                request.session['username'] = username
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request,'login.html')
    elif request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html')

def logout_user(request):
    del request.session['username']
    logout(request)
    return HttpResponseRedirect("login")

@login_required(login_url='login')
def with_csrf_token(request):
    if request.method == 'POST':
        csrf_input = request.POST.get('csrf_input','')
        return render(request,'csrf-output.html',{ 'csrf_input':csrf_input })
    elif request.method == 'GET':
        return render(request,'with-csrf-token.html')

# There is a restriction of HTTP that POST data cannot go with redirects.
# so CSRF POC won't work even with CSRF exempt with 302 http error
# we can test however for xss if we add the safe and escape attributes that prints the variable as is, unescaped
@csrf_exempt
@login_required(login_url='without_csrf_token')
def without_csrf_token(request):
    if request.method == 'POST':
        csrf_input = request.POST.get('csrf_input','')
        return render(request,'csrf-output-xss-poc.html',{ 'csrf_input':csrf_input })
        #return HttpResponseRedirect(request.GET.get('next'), { 'csrf_input' : csrf_input })
    elif request.method == 'GET':
        return render(request,'without-csrf-token.html')

class UploadFileForm(forms.Form):
    file = forms.FileField()

  
def handle_uploaded_file(f, username):
    # Check for file type by saving it in temp dir
    temp_file = tempfile.NamedTemporaryFile(delete=False,mode='wb+')
    print(temp_file.name)
    with temp_file as tmp:
        for chunk in f.chunks():
            tmp.write(chunk)
        tmp.close()
        get_file_type = magic.from_file(temp_file.name, mime=True)
        print(get_file_type)
        os.unlink(temp_file.name)
    # Upload file if magic has returned an image type
    if 'image' in get_file_type:
        with open(os.getcwd() + '\\static\\' + username + '.jpg', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
    else:
        print("Not an image: " + get_file_type)

@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            username = request.session['username']
            # image type can be obtained both from_buffer and from_file by using magic library
            content_type = magic.from_buffer(request.FILES['file'].read(), mime=True)
            print("content type from buffer: " + content_type)
            if 'image' in content_type:
                handle_uploaded_file(request.FILES['file'], username)
            return render(request, 'upload.html', {'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})