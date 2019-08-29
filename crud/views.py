from django.shortcuts import render, redirect
from .models import Order

# JSON 타입 반환을 위해 import
from django.http import JsonResponse
import json

#csrf 예외를 위해 import
from django.views.decorators.csrf import csrf_exempt

#주문정보를 저장하는 context입니다.
order_context = "<context 이름>"

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        req = json.loads(request.body)

        #request의 action을 파악합니다.
        action = req.get('queryResult').get('action')
        
        #params를 획득합니다.
        params = req.get('queryResult').get('parameters')

        # action에 따라서 이동합니다.
        if action == 'order_create-yes':
            return order_create(params)
        elif action == 'order_read':
            return order_read(params)
        elif action == 'order_update-yes':
            return order_update(params)
        elif action == 'order_delete-yes':
            return order_delete(params)
        elif action == 'order_delete-no':
            return order_delete_no(params)
            

def order_create(params):
    
    name = params.get('name')
    content = params.get('content')
    item = Order(name=name, content = content)
    item.save()
    
    # JSON 형식의 response 입니다.
    response = {
        'fulfillmentText' : '감사합니다. 주문번호는 {} 입니다.'.format(item.id),
          "outputContexts": [
            {
              "name": order_context,
              "lifespanCount": 3,
              "parameters": {
                "order_number": item.id
              }
            }
      ]
    }
    
    return JsonResponse(response, safe=False)
    # 주문 정보가 포함된 context를 함께 전송합니다.
    # 오류가 나지 않기 위해 'safe=False'가 필요합니다.
    
    
    
def order_read(params):
    order_number = params.get('order_number')
    item = Order.objects.get(pk=order_number)
    
    response = {'fulfillmentText': '{}님이 주문하신 내역은 {} 입니다.'.format(item.name, item.content),
                "outputContexts": [
                    {
                      "name": order_context,
                      "lifespanCount": 3,
                      "parameters": {
                        "order_number": item.id
                      }
                    }
                  ]
               }
    
    
    return JsonResponse(response, safe=False)
    
    
def order_update(params):
    order_number = params.get('order_number')
    
    # params로 들어온 content만을 수정합니다.
    item = Order.objects.get(pk=order_number)
    item.content = params.get('content')
    item.save()
    
    response = {'fulfillmentText': '성공적으로 수정되었습니다. {}님이 주문하신 내역은 {} 입니다.'.format(item.name, item.content),
                "outputContexts": [
                    {
                      "name": order_context,
                      "lifespanCount": 3,
                      "parameters": {
                        "order_number": item.id
                      }
                    }
                  ]
               }
    
    
    return JsonResponse(response, safe=False)


def order_delete(params):
    order_number = params.get('order_number')
    item = Order.objects.get(pk=order_number)
    item.delete()
    
    response = {'fulfillmentText': '성공적으로 삭제되었습니다.',
                "outputContexts": [
                    {
                      "name": order_context,
                      "lifespanCount": 0,
                    }
                  ]
               }
    
    # context의 lifespanCount를 0으로 주어서 context를 삭제합니다.
    return JsonResponse(response, safe=False)


def order_delete_no(params):
    # 삭제하지 않겠다는 응답을 한 경우의 response입니다.

    response = {
          "followupEventInput": {
            "name": "order_read",
            "languageCode": "ko"
          }
        }

    
    # Event를 발생시켜 주문 확인 intent를 불러오겠습니다.
    return JsonResponse(response, safe=False)