from django.http import HttpResponse
from django.shortcuts import render
import os
import json
from search import SearchManager

proc = SearchManager()

def index(request):
    return render(request,'index.html')

def hello(request):
    return HttpResponse("Hello world ! ")

def details(request):
    id=request.GET['id']
    # para={'id':id}
    para = {'id':id, 
    'title':'Wikipedia:Redirects for discussion/Log/2014 November 29', 
    'content':'-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi'
    }
    return render(request, 'details.html', para)


def search(request):
    # for test
    # data_type = request.POST['type'].strip()
    print(request)
    print(request.POST)
    search_type = int(request.POST['type'].strip())
    print('search_type:', search_type)
    query = request.POST['query'].strip()
    print(query)
    result_dict = proc.search(query)
    # print(result_dict)
    # test_dict = [
    #     { 'id':0,
    #         'title':'Wikipedia:Redirects for discussion/Log/2014 November 29', 
    #             'content':'-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi'},
    #     {'id':1,
    #         'title':'Wikipedia:Redirects for discussion/Log/2014 November 29', 
    #             'content':'-- Beland (talk) 15:47, 24 December 2014 (UTC)   * → Islam in Karachi'}]
    result_json = json.dumps(result_dict)
    return HttpResponse(result_json)


def sort(request):
    print(request)
    return HttpResponse("Hello, world.")