from __future__ import print_function
from datetime import datetime

import os.path
from enum import Enum

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from common.logger import logger
from maze_google_doc import settings


class ValidationException(Exception):
    """ Inappropriate argument value (of correct type). """

    def __init__(self, msg=''):  # real signature unknown
        Exception.__init__(self, msg)


class CheckParamMixin(object):
    """
    检查参数的view mixin
    """
    def validate_date(self, in_date_str, param_name, required=True):
        """
        验证时间参数有效性

        :param in_date_str: in date str
        :param required: 是否必须
        :param param_name: 参数名
        :return: date string
        """
        if not required and in_date_str is None:
            return None, None
        if required and not in_date_str:
            raise ValidationException(f'require parameter \'{param_name}\'')
        try:
            in_date = datetime.strptime(in_date_str, '%Y-%m-%d').date()
        except Exception:
            raise ValidationException(f'{param_name} format should be yyyy-mm-dd')
        return in_date_str, in_date

    def validate_common_data(self, in_data, param_name, required=True, default_value=None):
        """
        验证一般数据有效性

        :param in_data:
        :param param_name:
        :param required: 是否必须
        :param default_value: 默认值
        :return: 验证后的结果
        """
        value = in_data.get(param_name, default_value)
        # 需要先判断是否必须
        if required and (value is None or value == ''):
            raise ValidationException(f'{param_name} is required')
        if value == '':
            value = default_value
        return value

    def validate_start_end_date(self, in_data, start_date_param, end_date_param, required=True):
        """
        对开始和结束日期进行验证

        :param in_data:
        :param start_date_param:
        :param end_date_param:
        :param required: 是否必须
        :return: start_date_str, start_date, end_date_str, end_date
        """
        # 起止时间
        start_date_str, start_date = self.validate_date(
            in_data.get(start_date_param), start_date_param, required)
        end_date_str, end_date = self.validate_date(
            in_data.get(end_date_param), end_date_param, required)
        # 参数检查
        if start_date and end_date and start_date >= end_date:
            raise ValidationException('endDate must be later than startDate')
        return start_date_str, start_date, end_date_str, end_date

    def validate_sw_industry_level(self, request, field_name='level', default_value=1):
        """
        对传入的申万行业参数进行有效性验证

        :param request:
        :param field_name: 请求中对应该参数的参数名
        :param default_value: 默认值
        :return: 经过验证后的申万行业等级值
        """
        industry_level = request.query_params.get(field_name, default_value)
        try:
            industry_level = int(industry_level)
            if industry_level not in (1, 2):
                raise ValidationException()
        except Exception:
            raise ValidationException(f"parameter {field_name} should be 1 or 2")
        return industry_level

    def check_and_convert_str_params(self, in_value, param_name, required=True, default_value=None):
        """
        处理能转成数字的字符串或者数字

        :param in_value:
        :param param_name:
        :param required:
        :param default_value: 默认值
        :return: 验证后的结果
        """
        # 需要先判断是否必须
        if required and (in_value is None or in_value == ''):
            raise ValidationException(f'{param_name} is required')
        if in_value is None or in_value == '':
            return default_value
        try:
            int(in_value)
        except Exception:
            raise ValidationException(f"parameter {param_name} type error")
        return str(in_value)

    def check_and_convert_int_params(self, in_value, param_name, num_range=None, required=True, default_value=None):
        """
        处理int类型参数

        :param in_value: 值
        :param param_name: 参数名称
        :param num_range: 允许的数字范围, e.g num_range=(1,2)
        :param required:
        :param default_value: 默认值
        :return: 验证后的结果
        """
        # 需要先判断是否必须
        if required and (in_value is None or in_value == ''):
            raise ValidationException(f'{param_name} is required')
        if in_value is None or in_value == '':
            in_value = default_value
        try:
            in_value = int(in_value)
        except Exception:
            raise ValidationException(f"parameter {param_name} type error")
        if num_range is not None and in_value not in num_range:
            raise ValidationException(f"parameter {param_name} should be in {num_range}")
        return in_value

    def check_and_convert_float_params(self, in_value, param_name, required=True, default_value=None, num_range=None):
        """
        处理float类型参数

        :param in_value:
        :param param_name:
        :param required:
        :param default_value: 默认值
        :param num_range: 允许的数字范围, e.g num_range=range(0, 100)
        :return: 返回转化后的浮点数
        """
        # 需要先判断是否必须
        if required and (in_value is None or in_value == ''):
            raise ValidationException(f'{param_name} is required')
        if in_value is None or in_value == '':
            in_value = default_value
        try:
            in_value = float(in_value)
        except Exception:
            raise ValidationException(f"parameter {param_name} type error")
        if num_range is not None and not (num_range[0] <= in_value <= num_range[-1]):
            raise ValidationException(f"parameter {param_name} should be in {num_range}")
        return in_value

    def check_list(self, in_data, param_name, no_empty=True):
        """
        对传入的列表进行验证

        :param in_data: request.data
        :param param_name: 参数名
        :param no_empty: 是否一定要求非空
        :return: 验证后的list
        """
        result = in_data.get(param_name)
        if result is None or (not result and no_empty) or not isinstance(result, list):
            raise ValidationException(f'invalid value of {param_name}')
        return result

    def validate_boolean_params(self, in_value, param_name, default_value=None):
        """
        validate布尔值参数, 1为True, 0为False

        :param in_value:
        :param param_name: 字段名
        :param default_value: 如果value为空且default_value不为空，返回default_value
        :return: 该字段对应的值或返回default_value
        """
        if in_value is None:
            if default_value is not None:
                return default_value
            else:
                raise ValidationException(f'parameter {param_name} is required, should be 1, true, t or 0, false, f')
        in_value = str(in_value).lower()
        if in_value in ('1', 'true', 't'):
            return True
        elif in_value in ('0', 'false', 'f'):
            return False

        raise ValidationException(f'parameter {param_name} should be 1, true, t or 0, false, f')


class GoogleAuthType(Enum):
    SERVICE_ACCOUNT_KEY = 1
    DESKTOP_OAUTH2 = 2


class ResponseCode(Enum):
    SUCCESS = 200
    # 已分析出原因的错误
    REGULAR_ERROR = 400
    # 未知错误
    UNKNOWN_ERROR = 500


class GoogleDocOperator(object):
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/drive.file']

    def __init__(self, auth_type=GoogleAuthType.SERVICE_ACCOUNT_KEY):
        self.doc_service = None
        self.drive_service = None
        creds = None
        if auth_type == GoogleAuthType.DESKTOP_OAUTH2:
            # 桌面的OAUTH2认证,
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists(settings.GOOGLE_PROJECT_TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(settings.GOOGLE_PROJECT_TOKEN_FILE, self.SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.GOOGLE_PROJECT_CREDENTIALS_FILE, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(settings.GOOGLE_PROJECT_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
        elif auth_type == GoogleAuthType.SERVICE_ACCOUNT_KEY:
            # web server的 service account认证
            # 获取访问凭证
            creds = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_CREDENTIALS_FILE, scopes=self.SCOPES)

        try:
            self.doc_service = build('docs', 'v1', credentials=creds)
        except HttpError as err:
            logger.exception(f'build google doc api service failed, {err}')
            raise err

        try:
            self.drive_service = build('drive', 'v3', credentials=creds)
        except HttpError as err:
            logger.exception(f'build google drive api service failed, {err}')
            raise err

    def _get_webvie_link(self, doc_id):
        """
        通过文件id返回http链接

        :param doc_id:
        :return: http链接
        """
        if not self.drive_service:
            raise ValueError('no available drive service')
        file = self.drive_service.files().get(fileId=doc_id, fields='webViewLink').execute()
        return file.get('webViewLink')

    def create_doc(self, title, username, direct_folder):
        """
        根据username 和 direct_folder在指定位置新建一个文件名为title新文件

        :param title: 目标文件文件名
        :param username: user name
        :param direct_folder: 目标文件的直接父文件夹名称
        :return: 生成文件file id，生成文件link
        """
        doc_id = None
        try:
            folder_id = self.get_or_create_folder([username, direct_folder])
            if not folder_id:
                raise ValueError(f'failed to create folder {username} for doc {title}')

            document = self.doc_service.documents().create(body={'title': title}).execute()
            logger.info(f'create_doc: first request for creating title {title}, response is {document}')
            doc_id = document.get('documentId')
            if not doc_id:
                logger.error('creat the document failed')
                return None

            # copy到对应google drive目录下
            body = {
                'name': title,
                'parents': [folder_id]
            }
            drive_response = self.drive_service.files().copy(fileId=doc_id, body=body).execute()
            document_copy_id = drive_response.get('id')
            return document_copy_id, self._get_webvie_link(document_copy_id)
        finally:
            # 删除第一个出现在默认位置的文档
            try:
                if doc_id:
                    self.drive_service.files().delete(fileId=doc_id).execute()
                    logger.info(f'File with ID {doc_id} has been deleted successfully.')
            except Exception as e:
                logger.exception(f'An error occurred while deleting the file id {doc_id}: {e}')

    def get_parent_folders(self, file_id):
        """
        获得google doc指定文件（夹）的父文件夹列表file id 列表

        :param file_id:
        :return: 文件夹列表file id 列表
        """
        file = self.drive_service.files().get(fileId=file_id, fields='parents').execute()
        parents = file.get('parents')
        return parents

    def make_copy(self, source_file_id, new_tile):
        """
        在同文件夹对指定文件做一份拷贝，文件名为new_tile

        :param source_file_id: 源文件
        :param new_tile: 新文件名
        :return: 生成文件file id，生成文件link
        """
        folder_id = None
        parents = self.get_parent_folders(source_file_id)
        if parents:
            folder_id = parents[0]
        if not folder_id:
            raise ValueError(f'failed to create folder to make copy for doc: {new_tile}')
        # copy到对应google drive目录下
        body = {
            'name': new_tile,
            'parents': [folder_id]
        }
        drive_response = self.drive_service.files().copy(fileId=source_file_id, body=body).execute()
        document_copy_id = drive_response.get('id')
        return document_copy_id, self._get_webvie_link(document_copy_id)

    def get_doc(self, doc_id):
        """
        根据doc id返回google doc api 对此doc的get结果

        :param doc_id: doc id
        :return: 形如：
        {'title': '文书测试', 'body': {'content': ..., ..}, 'documentStyle': .. ,
        'namedStyles': .., 'revisionId': 'ANeT5PQ1_xnZmnAbW2MeoOK8ldgtpps2xvoFpvez8qpeGsbb2jTMNzzQrAz4pfb9iu',
        'suggestionsViewMode': 'SUGGESTIONS_INLINE', 'documentId': '1IUDZmR0P9Z0AdWTnZnL12kJrMHMVl7pA1bU6p2gkeCU'}
        """
        document = self.doc_service.documents().get(documentId=doc_id).execute()
        return document

    def get_or_create_folder(self, folder_list, parent_folder_id=settings.DOC_ROOT_FOLDER_ID):
        """
        在指定的parent folder下面查找指定名称的folder,没有则进行创建，返回目标folder的file id
        假定parent folder下最多只有一个名称为folder_name的目录

        :param folder_list: 查找或创建的目录名称列表，从左至右目录层次由高到底
        :param parent_folder_id: 直接父目录
        :return: 目标folder的file id
        """
        if len(folder_list) == 1:
            folder_name = folder_list[0]
            print('aaaa')
            print(parent_folder_id)
            # 假设只有一个符合结果，目前
            response = self.drive_service.files().list(
                q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and "
                  f"'{parent_folder_id}' in parents", spaces='drive', fields='files(id, name)').execute()
            if response.get('files'):
                return response['files'][0]['id']

            logger.info(f'no folder named {folder_name} under file ID {parent_folder_id}， creating...')
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }

            file = self.drive_service.files().create(body=file_metadata, fields='id').execute()
            result = file.get('id')
            if result:
                logger.info(f'created {folder_name} under folder with file id {parent_folder_id}, '
                            f'target folder id: {result}')
            else:
                logger.info(f'failed to create {folder_name} under folder with file id {parent_folder_id}')
            return result
        else:
            current_folder_id = parent_folder_id
            for folder_name in folder_list:
                current_folder_id = self.get_or_create_folder([folder_name], current_folder_id)
                if not current_folder_id:
                    return None
            logger.info(f'finished creating folder for {folder_list}')
            return current_folder_id


if __name__ == '__main__':
    operator = GoogleDocOperator(GoogleAuthType.SERVICE_ACCOUNT_KEY)
    # print(operator.get_or_create_folder(['aaaa', 'bbb']))
    print(operator.create_doc('测试测试22223', 'aaaa', 'bbb'))
    # operator.create_doc('测试测试22223')
    # operator.make_copy('1Ce_tVb_GAAZa4L3GtlGXJ465n-Ur--GOp1hxPIpMOXI', 'copy_测试')
    # result = operator.get_doc('1sCMo-JFAbOcF-6qpExGeurF26za7LkMh_oiGooYnAFI')
    # print(result)
    # print(result.keys())
    # print(operator.create_doc('service account test'))
    # result = operator.get_doc('1_Uj90jsGoUVSR262FYcHC-8tzkugYD6bsYTm_YrV9FM')
    # print(result)
    # test_create('测试测试111111')
