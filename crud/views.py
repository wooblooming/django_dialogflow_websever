from django.shortcuts import render, redirect

#csrf 예외를 위해 import
from django.views.decorators.csrf import csrf_exempt

# JSON 타입 반환을 위해 import
from django.http import JsonResponse
import json

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        req = json.loads(request.body)

        #request의 action을 파악합니다.
        action = req.get('queryResult').get('action')
        

        # action에 따라서 이동합니다.
        # if action == 'order_destroy':
        #     params = req.get('queryResult').get('parameters')
        #     return order_destroy(request, params)

