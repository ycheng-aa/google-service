from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.logger import logger
from common.utils import CheckParamMixin, ValidationException, ResponseCode, GoogleDocOperator, GoogleAuthType


class NewDocView(APIView, CheckParamMixin):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Run:
            curl -H 'Authorization: Token xxx' -H "Content-Type: application/json" --request GET http://127.0.0.1:8000/api/v1/new_doc/?username=student1\&title=%E5%AD%A6%E7%94%9F%E6%96%87%E4%B9%A61\&folder=dukeabaacde

        you will get a `Response` like:
            {
                "code": 200,   // 其余代码代表失败
                "message": "ok",
                "data": {
                    "doc_id": "12AjXbkTk-_u4EMavRzhVzdQ8RifApJ7GkruZN30GGX4",
                    "web_link": "https://docs.google.com/document/d/12AjXbkTk-_u4EMavRzhVzdQ8RifApJ7GkruZN30GGX4/edit?usp=drivesdk"
                }
            }
        """  # noqa
        try:
            in_data = request.query_params
            logger.info(in_data)
            for field in ('username', 'title', 'folder'):
                self.validate_common_data(in_data, field)

            operator = GoogleDocOperator(GoogleAuthType.SERVICE_ACCOUNT_KEY)
            doc_id, web_link = operator.create_doc(in_data['title'], in_data['username'], in_data['folder'])
            result = {'code': ResponseCode.SUCCESS.value, 'message': 'ok',
                      'data': {'doc_id': doc_id, 'web_link': web_link}}
            return Response(result)
        except ValidationException as e:
            return Response({'code': ResponseCode.REGULAR_ERROR.value, 'message': str(e)})
        except Exception as e:
            logger.exception(str(e))
            return Response({'code': ResponseCode.UNKNOWN_ERROR.value, 'message': settings.UNKNOWN_ERROR_RESP_PROMPT})


class CopyDocView(APIView, CheckParamMixin):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Run:

            curl -H 'Authorization: Token xxxx' -H "Content-Type: application/json" --request GET http://127.0.0.1:8000/api/v1/copy_doc/?title=%E8%80%81%E5%B8%88%E4%BF%AE%E6%94%B95\&source_doc_id=1YwBFXg_moYpgyOQ_74DnPxbDKnY7XWYj7vcnLNb8ks8

        you will get a `Response` like:
            {
                "code":200, // 其余代码代表失败
                "message":"ok",
                "data":{
                    "target_doc_id":"1tVYBras4yJEEHdhx2mkH2SOJ8ATzzvpMEnMYfoAIS20",
                    "web_link":"https://docs.google.com/document/d/1tVYBras4yJEEHdhx2mkH2SOJ8ATzzvpMEnMYfoAIS20/edit?usp=drivesdk"
                    }
                }
        """  # noqa
        try:
            in_data = request.query_params
            for field in ('source_doc_id', 'title'):
                self.validate_common_data(in_data, field)

            operator = GoogleDocOperator(GoogleAuthType.SERVICE_ACCOUNT_KEY)
            target_doc_id, web_link = operator.make_copy(in_data['source_doc_id'], in_data['title'])
            result = {'code': ResponseCode.SUCCESS.value, 'message': 'ok',
                      'data': {'target_doc_id': target_doc_id, 'web_link': web_link}}
            return Response(result)
        except ValidationException as e:
            return Response({'code': ResponseCode.REGULAR_ERROR.value, 'message': str(e)})
        except Exception as e:
            logger.exception(str(e))
            return Response({'code': ResponseCode.UNKNOWN_ERROR.value, 'message': settings.UNKNOWN_ERROR_RESP_PROMPT})
