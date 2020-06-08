from django import template
from django.db.models import Sum
from django.urls import reverse

from mysite import settings
from order.models import ShopCart
from product.models import Category

register = template.Library()


@register.simple_tag
def categorylist():
    return Category.objects.all()


@register.simple_tag
def shopcartcount(userid):
    count = ShopCart.objects.filter(user_id=userid).count()
    return count

# views-> "category =  categoryTree(0,'','tr')"  html-> "ategoryTree 0 '' LANGUAGE_CODE as category"
@register.simple_tag
def categoryTree(id,menu,lang):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    #lang='tr'
    if id <= 0: # Main categories
        if lang == defaultlang: # default language
            query = Category.objects.filter(parent_id__isnull=True).order_by("id")
        else: # non default language
            query = Category.objects.raw('SELECT c.id,l.title, l.keywords, l.description,l.slug' 
                                      '  FROM product_category as c'
                                      '  INNER JOIN product_categorylang as	l'
                                      '  ON c.id = l.category_id'
                                      '  WHERE  parent_id IS NULL and lang=%s ORDER BY c.id',[lang])
        querycount = Category.objects.filter(parent_id__isnull=True).count()
    else: # Sub Categories
        if lang == defaultlang: # default language
            query = Category.objects.filter(parent_id=id)
        else: # non default language
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
                menu += '\t<a class ="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">'+ rs.title +'<i class="fa fa-angle-right"></i></a>\n'
                menu += '\t\t<div class="custom-menu">\n'
                menu += '\t\t\t<ul class="list-links">\n'
                menu += categoryTree(int(rs.id),'',lang)
                menu += '\t\t\t</ul>\n'
                menu += '\t\t</div>\n'
                menu += "\t</li>\n\n"
            else :
                menu += '\t\t\t\t<li><a href="'+reverse('category_products',args=(rs.id, rs.slug)) +'">' + rs.title + '</a></li>\n'
    return menu