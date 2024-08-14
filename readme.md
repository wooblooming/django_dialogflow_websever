# Django Dialogflow Websever

django를 이용해 google dialogflow 의 fulfillment 기능을 이용할 수 있는 샘플 코드입니다. dialogflow 챗봇을 활용해 django 모델 CRUD (create, read, update, delete)를 할 수 있게 코드를 작성해 두었습니다.


 <a href="https://ymgym.github.io/%EC%95%84%ED%94%88%EC%A7%80%EB%A0%81%EC%9D%B4/2019/08/13/dialogflow(1).html">여기</a>


## 코드 구성

이 앱은 dialogflow의 핵심 기능들을 알아보는 것에 중점을 둡니다.
강의의 편의를 위해 버그를 일으킬 수 있는 요소들을 수정하지 않은 상태입니다. 따라서 실사용 시에는 이 코드를 기반으로 더 정교한 설계를 하는 것을 추천 드립니다.

### app 구성

`dialogflow_project` 프로젝트 안에 `crud` 앱을 만들고, `settings.py`에 추가 해 둔 상태입니다.

프로젝트 `urls.py` 에서 `webhook/` 으로 받은 리퀘스트를 `crud` 앱으로 전송합니다. `crud` 에서는 `webhook/` 으로 바로 들어오는 리퀘스트 이외에 어떠한 url도 등록되어 있지 않습니다.

### model 구성

샘플 모델로 주문자의 정보와 내용을 저장하는 `Order` 모델을 작성해 두었습니다. 

`Order` 모델에는 주문자의 이름을 작성하는 `name` 열과, 주문 내용(주문한 제품)을 기록하는 `content` 열로 저장되어 있으며, `__str__` 함수를 통해 admin 페이지에서 주문자의 이름으로 나타나도록 설정해 두었습니다.

`Order` 모델은 admin 페이지에 register 되어 있습니다.

### View 구성

`views.py` 에는 JSON타입 반환과 CSRF 토큰 오류를 방지하기 위해 다음과 같은 코드가 들어 있습니다.

~~~python
...
# JSON 타입 반환을 위해 import
from django.http import JsonResponse
import json

#csrf 예외를 위해 import
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
...
~~~
## CRUD

CRUD 각 기능 별 설명이 적힌 dialogflow의 요소들은 다음과 같습니다.
Create
> fulfillment 연결, parameters, action

Read
> context

Update
>    없음.

Delete
> follow-up context, context 삭제, event,


## Code 설명

`views.py`의 action별로 나눠서 설명하도록 하겠습니다.

### webhook

`webhook()` 에서는 request를 POST형식으로 받아 각 액션으로 전송합니다.

이를 위해 dialogflow 콘솔에서 fulfillment 탭에 Webhook 을 활성화 시키고, URL을 입력해 주어야 합니다.

`action` 변수에 action 명을 담아서 intent를 구분합니다. 

`params` 변수에 request의 parameters를 담아 action으로 매개변수를 통해 전송합니다.

### order_create

params 매개변수를 통해 전송받은 데이터를 `Order` 모델에 저장합니다. 이를 통해 dialogflow에서 parameters를 다음과 같이 설정해야 합니다.

~~~JSON
...
"parameters": {
      "name": "[주문자 이름]",
      "content": "[주문된 상품]"
    },
...
~~~

`order_create()` 로 연결되는 action은 `order_create` 이기 때문에, 주문 생성 intent의 action을 같게 설정해야 합니다.

create 에는 `outputContexts` 요소를 사용해 모델 id를 포함한 context를 반환하는 context가 주석처리 되어 있습니다. 해제하여 사용하면 create에도 context를 반환하게 됩니다.
기본적으로는 강의의 진행 편의를 위해 주석처리 되어 있습니다.

### order_read

`order_context`의 `order_number` 요소를 사용해 데이터를 read합니다.
context가 존재하지 않으면, prompt를 사용해 parameters를 직접 획득하도록 할 수 있습니다.

Response에는 `outputContexts`를 통해 context를 반환하고, 파라미터로 `order_number`를 넘깁니다. 읽은 주문의 id값을 포함합니다.


### order_update

parameters로 전송된 속성을 사용해 update합니다.
parameters는 다음과 같습니다.

~~~json
...
"parameters": {
      "order_number": "[(int)order_number]",
      "content": "[수정된 주문 내용]"
    }
...
~~~

Read와 똑같이 context를 반환합니다.

### order_delete

Delete는 follow-up intent를 사용해 yes 와 no로 구분됩니다.

#### yes
yes의 경우 parameters를 통해 delete를 수행합니다.
follow-up intent인 경우에도 삭제를 수행하기 위해 parameters값에 order_number 을 주어야 합니다.

삭제 후 id값을 포함한 context를 모두 삭제해야 하기 때문에 `lifespan`을 0으로 주어 context를 삭제합니다.

~~~json
...
response = {'fulfillmentText': '성공적으로 삭제되었습니다.',
                "outputContexts": [
                    {
                      "name": order_context,
                      "lifespanCount": 0,
                    }
                  ]
               }
...
~~~

#### no
no 의 경우에는 `order_delete-no` 액션으로 이동합니다.
이 액션에서는 response를 반환하지 않고, event를 활용해 view intent로 이동시킵니다.

 response는 다음과 같습니다
~~~json
...
response = {
          "followupEventInput": {
            "name": "order_read",
            "languageCode": "ko"
          }
        }
...
~~~

이를 위해 order_view intent의 event를 order_read로 설정할 필요가 있습니다.



## 기타
강의에 사용한 프레젠테이션 파일은 이 레포지토리에 포함되어 있습니다(presentation.pdf)

