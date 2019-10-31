from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template, render_to_string


def custom_css(request):
    template = get_template('users/user_style.css')
    context = {
        'user': request.user,
    }
    return HttpResponse(template.render(context, request), content_type="text/plain")
