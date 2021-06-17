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
    print('id is ', id)
    page = proc.read_page(id)
    for terms in page['terms']:
        print(terms)
        page['content'] = page['content'].replace(
            f"{terms}", f"<font color='red'><b>{terms}</b></font>")
    para = {'id': id, 'title': page['title'], 'content': page['content']}
    return render(request, 'details.html', para)


def search(request):
    search_type = int(request.POST['type'].strip())
    print('search_type:', search_type)
    query = request.POST['query'].strip()
    print(query)
    page_list, time_str, querys, n_searched = proc.search(query, rank_mode=search_type)

    para = {
        'pages': page_list,
        'time': time_str,
        'querys': querys,
        'n_searched': n_searched
    }
    result_json = json.dumps(para)
    return HttpResponse(result_json)


def sort(request):
    print(request)
    return HttpResponse("Hello, world.")