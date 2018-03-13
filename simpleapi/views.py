# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: views.py
# @Last modified by:   valle
# @Last modified time: 10-Mar-2018
# @License: Apache license vesion 2.0


from django.conf import settings
from tokenapi.decorators import token_required
from django.views.decorators.csrf import csrf_exempt
from tokenapi.http import JsonResponse, JsonError
from .simplex_db import Model, QSonHelper as QSonHelperDjango
import json

# Create your views here.
@csrf_exempt
def qson_django(request):
    if request.method != 'POST' or not 'data' in request.POST:
        return JsonError("Este servidor solo acepta peticiones POST")
    data = json.loads(request.POST.get("data"))
    JSONResponse = {}
    qson_helper = QSonHelperDjango()
    JSONResponse = qson_helper.decode_qson(data)
    http = JsonResponse(JSONResponse)
    return http



@token_required
def getfiles(request):
    if request.method != 'POST' or not 'ID' in request.POST:
        return JsonError("Este servidor solo acepta peticiones POST")

    id_file = request.POST["ID"]
    path = FileController.getPath(id_file)
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    return JsonError("Pagina no encontrada o un error inesperado")


def email(datos, JSONResponse):
    from django.core.mail import send_mail
    try:
        send_mail(datos.get("subject"), datos.get("men"), datos.get("from"),
                  [datos.get("to")], fail_silently=False)
        JSONResponse["send_mail"] = {"success": True}
    except:
        JSONResponse["send_mail"] = {"success": False}
