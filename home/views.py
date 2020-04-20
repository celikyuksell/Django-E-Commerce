from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from home.models import Setting, ContactForm, ContactMessage
from product.models import Category, Product


def index(request):
    setting = Setting.objects.get(pk=1)
    category = Category.objects.all()
    products_slider = Product.objects.all().order_by('id')[:4]  #first 4 products
    products_latest = Product.objects.all().order_by('-id')[:4] #last 4 products
    products_picked = Product.objects.all().order_by('?')[:4]   #Random selected 4 products

    page="home"
    context={'setting':setting,
             'page':page,
             'products_slider': products_slider,
             'products_latest': products_latest,
             'products_picked': products_picked,
             'category':category }
    return render(request,'index.html',context)


def aboutus(request):
    setting = Setting.objects.get(pk=1)
    context={'setting':setting }
    return render(request, 'about.html', context)

def contactus(request):
    if request.method == 'POST': # check post
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage() #create relation with model
            data.name = form.cleaned_data['name'] # get form input data
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  #save data to table
            messages.success(request,"Your message has ben sent. Thank you for your message.")
            return HttpResponseRedirect('/contact')

    setting = Setting.objects.get(pk=1)
    form = ContactForm
    context={'setting':setting,'form':form }
    return render(request, 'contactus.html', context)

def category_products(request,id,slug):
    category = Category.objects.all()
    products = Product.objects.filter(category_id=id)
    context={'products': products,
             'category':category }
    return render(request,'category_products.html',context)