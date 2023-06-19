# 通用说明
* 此项目提供google doc相关操作的服务

## 配置
* 使用Python 3.10.11或更高版本
* 安装依赖：`pip install -r requirements/devel.txt`
* 在resources目录下放入用来访问google资源的google service account的API KEY，命名为service-account-credentials.json；该账号需要有必要的文档和google drive权限
* 各敏感信息的配置都可以用 settings.py 平级的 settings_local.py 进行覆盖；上面的提到api_key位置为GOOGLE_SERVICE_ACCOUNT_CREDENTIALS_FILE, 文档所在根目录ID为DOC_ROOT_FOLDER_ID
* 数据库配置项为DATABASES
* 项目使用Django开发，使用 `python manage.py migrate` 和  `python manage.py runserver ip:端口号` 进行migrate和启动服务; 也可以使用gunicorn等各种组件启动服务
* 使用 `python manage.py runserver ip:端口号` 启动http服务 或者 `python manage.py runsslserver ip:端口号` 启动https服务
* 使用 `python manage.py createsuperuser` 创建超级用户；还可以随后使用django shell创建各个用户

## 使用接口
* 登录获得token, 形如 `curl -H "Content-Type: application/json" --request POST "http://127.0.0.1:8000/api/v1/login/"  -d '{"username": "xxx", "password": "xxx"}'`
* 根据返回的token，在访问请求的header上加入 `Authorization: Token 取得的token`，然后正常访问各个接口即可
* token不对或失效时会返回http code 403
* 如果访问的为https服务可以为 `curl` 命令加上 `-k`参数
