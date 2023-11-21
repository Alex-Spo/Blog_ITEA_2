from django.core.paginator import Paginator
from django.shortcuts import render

from blog import models


def post_list_view(request):
    posts = models.Post.objects.all()

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post/post_list.html', {'page_obj': page_obj, 'posts': posts})

