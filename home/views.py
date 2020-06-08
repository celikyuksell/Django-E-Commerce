import json

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from django.shortcuts import render

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation

from home.forms import SearchForm
from home.models import Setting, ContactForm, ContactMessage, FAQ, SettingLang
from mysite import settings
from product.models import Category, Product, Images, Comment, Variants, ProductLang, CategoryLang

def categoryTree(id,menu,lang):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    #lang='tr'
    if id <= 0:
        if lang == defaultlang:
            query = Category.objects.filter(parent_id__isnull=True).order_by("id")
        else:
            query = Category.objects.raw('SELECT c.id,l.title, l.keywords, l.description,l.slug' 
                                      '  FROM product_category as c'
                                      '  INNER JOIN product_categorylang as	l'
                                      '  ON c.id = l.category_id'
                                      '  WHERE  parent_id IS NULL and lang=%s ORDER BY c.id',[lang])
        querycount = Category.objects.filter(parent_id__isnull=True).count()
    else:
        if lang == defaultlang:
            query = Category.objects.filter(parent_id=id)
        else:
            query = Category.objects.raw('SELECT c.id,l.title, l.keywords, l.description,l.slug'
                                     '  FROM product_category as c'
                                     '  INNER JOIN product_categorylang as	l'
                                     '  ON c.id = l.category_id'
                                     '  WHERE  parent_id =%s AND lang=%s', [id,lang])
        querycount = Category.objects.filter(parent_id= id).count()
    if querycount > 0:
        for rs in query:
            subcount = Category.objects.filter(parent_id=rs.id).count()
            if subcount > 0:
                menu += '\t<li class="dropdown side-dropdown">\n'
                menu += '\t<a class ="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">'+ rs.title   + '<i class="fa fa-angle-right"></i></a>\n'
                menu += '\t\t<div class="custom-menu">\n'
                menu += '\t\t\t<ul class="list-links">\n'
                menu += categoryTree(int(rs.id),'',lang)
                menu += '\t\t\t</ul>\n'
                menu += '\t\t</div>\n'
                menu += "\t</li>\n\n"
            else :
                menu += '\t\t\t\t<li><a href="'+reverse('category_products',args=(rs.id, rs.slug)) +'">' + rs.title + '</a></li>\n'
    return menu

def index(request):
    currentlang = request.LANGUAGE_CODE[0:2]
    #category = categoryTree(0,'',currentlang)

    # category = categoryTree(0, '', currentlang)


    setting = Setting.objects.get(pk=1)
    products_latest = Product.objects.all().order_by('-id')[:4]  # last 4 products
    # >>>>>>>>>>>>>>>> M U L T I   L A N G U G A E >>>>>> START
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]

    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)
        products_latest = Product.objects.raw(
            'SELECT p.id,p.price, l.title, l.description,l.slug  '
            'FROM product_product as p '
            'LEFT JOIN product_productlang as l '
            'ON p.id = l.product_id '
            'WHERE  l.lang=%s ORDER BY p.id DESC LIMIT 4', [currentlang])

    products_slider = Product.objects.all().order_by('id')[:4]  #first 4 products


    products_picked = Product.objects.all().order_by('?')[:4]   #Random selected 4 products

    page="home"
    context={'setting':setting,
             'page':page,
             'products_slider': products_slider,
             'products_latest': products_latest,
             'products_picked': products_picked,
             #'category':category
             }
    return render(request,'index.html',context)




def selectlanguage(request):
    if request.method == 'POST':  # check post
        cur_language = translation.get_language()
        lasturl= request.META.get('HTTP_REFERER')
        lang = request.POST['language']
        translation.activate(lang)
        request.session[translation.LANGUAGE_SESSION_KEY]=lang
        #return HttpResponse(lang)
        return HttpResponseRedirect("/"+lang)

def aboutus(request):
    #category = categoryTree(0,'',currentlang)
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    setting = Setting.objects.get(pk=1)
    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)

    context={'setting':setting}
    return render(request, 'about.html', context)

def contactus(request):
    currentlang = request.LANGUAGE_CODE[0:2]
    #category = categoryTree(0,'',currentlang)
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

    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    setting = Setting.objects.get(pk=1)
    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)

    form = ContactForm
    context={'setting':setting,'form':form  }
    return render(request, 'contactus.html', context)

def category_products(request,id,slug):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    catdata = Category.objects.get(pk=id)
    products = Product.objects.filter(category_id=id) #default language
    if defaultlang != currentlang:
        try:
            products = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s and l.lang=%s', [id, currentlang])
        except:
            pass
        catdata = CategoryLang.objects.get(category_id=id, lang=currentlang)

    context={'products': products,
             #'category':category,
             'catdata':catdata }
    return render(request,'category_products.html',context)

def search(request):
    if request.method == 'POST': # check post
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query'] # get form input data
            catid = form.cleaned_data['catid']
            if catid==0:
                products=Product.objects.filter(title__icontains=query)  #SELECT * FROM product WHERE title LIKE '%query%'
            else:
                products = Product.objects.filter(title__icontains=query,category_id=catid)

            category = Category.objects.all()
            context = {'products': products, 'query':query,
                       'category': category }
            return render(request, 'search_products.html', context)

    return HttpResponseRedirect('/')

def search_auto(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)

        results = []
        for rs in products:
            product_json = {}
            product_json = rs.title +" > " + rs.category.title
            results.append(product_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def product_detail(request,id,slug):
    query = request.GET.get('q')
    # >>>>>>>>>>>>>>>> M U L T I   L A N G U G A E >>>>>> START
    defaultlang = settings.LANGUAGE_CODE[0:2] #en-EN
    currentlang = request.LANGUAGE_CODE[0:2]
    #category = categoryTree(0, '', currentlang)
    category = Category.objects.all()

    product = Product.objects.get(pk=id)

    if defaultlang != currentlang:
        try:
            prolang =  Product.objects.raw('SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                                          'FROM product_product as p '
                                          'INNER JOIN product_productlang as l '
                                          'ON p.id = l.product_id '
                                          'WHERE p.id=%s and l.lang=%s',[id,currentlang])
            product=prolang[0]
        except:
            pass
    # <<<<<<<<<< M U L T I   L A N G U G A E <<<<<<<<<<<<<<< end

    images = Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id,status='True')
    context = {'product': product,'category': category,
               'images': images, 'comments': comments,
               }
    if product.variant !="None": # Product have variants
        if request.method == 'POST': #if we select color
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(id=variant_id) #selected product by click color radio
            colors = Variants.objects.filter(product_id=id,size_id=variant.size_id )
            sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id',[id])
            query += variant.title+' Size:' +str(variant.size) +' Color:' +str(variant.color)
        else:
            variants = Variants.objects.filter(product_id=id)
            colors = Variants.objects.filter(product_id=id,size_id=variants[0].size_id )
            sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id',[id])
            variant =Variants.objects.get(id=variants[0].id)
        context.update({'sizes': sizes, 'colors': colors,
                        'variant': variant,'query': query
                        })
    return render(request,'product_detail.html',context)

def ajaxcolor(request):
    data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string('color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)


def faq(request):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    category = categoryTree(0, '', currentlang)
    if defaultlang==currentlang:
        faq = FAQ.objects.filter(status="True",lang=defaultlang).order_by("ordernumber")
    else:
        faq = FAQ.objects.filter(status="True",lang=currentlang).order_by("ordernumber")

    context = {
        'category': category,
        'faq': faq,
    }
    return render(request, 'faq.html', context)