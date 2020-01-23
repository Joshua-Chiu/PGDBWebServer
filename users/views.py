from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template, render_to_string


def personalisation(request):
    template = get_template('users/personalisation.html')
    context = {
        'user': request.user
    }
    return HttpResponse(template.render(context, request))


def personalisation_submit(request):
    user = request.user
    data = request.POST

    for key, value in data.items():
        if key != 'csrfmiddlewaretoken':
            setattr(user, key, value)
            # print(f"{user}| {key}: {value}")
            user.save()

    return HttpResponseRedirect('/users/personalisation')


def autofocus_submit(request, num):
    user = request.user
    user.autofocus = num
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
