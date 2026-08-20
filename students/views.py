from django.http import HttpResponse

def home(request):
    return HttpResponse("Hy, welcome to the Students app!")
from django.shortcuts import render

def home(request):
    return render(request, 'students/home.html')