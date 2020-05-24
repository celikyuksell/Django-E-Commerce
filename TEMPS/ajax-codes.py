
def ajaxtest(request):
    posts = Comment.objects.all()
    response_data = {}

    if request.POST.get('action') == 'post':
        title = request.POST.get('title')
        description = request.POST.get('description')

        response_data['title'] = title
        response_data['description'] = description
        data= Comment()
        data.product_id=1
        data.user_id=1
        data.rate=3
        data.subject=title
        data.comment=description
        data.save()
        return JsonResponse(response_data)
    return render(request,'AjaxTest.html', {'posts':posts})

def ajaxpost(request):
    response_data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid,size_id=size_id )
        context = {
            'colors': colors,
            'size_id': size_id,
        }
        data = {'rendered_table': render_to_string('color_list.html', context=context)}
        return JsonResponse(data)

    sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
    colors = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY color_id', [id])
    context ={  'sizes': sizes,
                'colors': colors,

                }
    return render(request, 'AjaxTest2.html', context)
#data = {'rendered_table': render_to_string('table_contents.html', context=context)}
# return JsonResponse(response_data)


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

def ajaximage(request):
    return None


def ajaxSelectedProduct(request):
    data = {}
    if request.POST.get('action') == 'post':
        variantid = request.POST.get('variant')
        varproduct = Variants.objects.get(id=variantid)
        context = {
            'varproduct': varproduct,
            'variantid': variantid,
        }
        data = {'rendered_data': render_to_string('selected_product.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)