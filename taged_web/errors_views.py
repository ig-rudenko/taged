from django.shortcuts import render


def page404(request, exception):
    return render(request, "errors/404.html", status=404)


def page500(request, *args, **kwargv):
    return render(request, "errors/500.html", status=500)
