from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template

def index(request):
	template = get_template('test3/index.html')
	context = {
	}

	return HttpResponse(template.render(context, request))

