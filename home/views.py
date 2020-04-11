from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    university="Karabuk University"
    dept="Computer Engineering"
    context={'university':university, 'department':dept }
    return render(request,'index.html',context)
