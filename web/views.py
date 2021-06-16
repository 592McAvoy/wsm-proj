from django.http import HttpResponse
from django.shortcuts import render
import os
import json
from search import SearchManager

proc = SearchManager()


def index(request):
    return render(request, 'index.html')


def details(request):
    id = int(request.GET['id'])
    page = proc.read_page(id)
    print('id is ', id)
    page['content'] = page['content'].replace(" Art ", "<font color='red'><b> Art </b></font>")
    para = {'id': id, 'title': page['title'], 'content': page['content']}
    return render(request, 'details.html', para)


def search(request):
    search_type = int(request.POST['type'].strip())
    print('search_type:', search_type)
    query = request.POST['query'].strip()
    print(query)
    page_list, time_str, querys = proc.search(query)

    para = {'pages': page_list, 'time': time_str, 'querys': querys}
    result_json = json.dumps(para)
    return HttpResponse(result_json)


def sort(request):
    print(request)
    return HttpResponse("Hello, world.")