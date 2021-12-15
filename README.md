# javaEeAccessControlCheck
Check broken access control exists in the Java web application.

检查 Java Web 应用程序中是否存在访问控制绕过问题。

# 使用
```
python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index?id=1"
python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index" -data id=1
python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index" -data-json '{"id":1}'
python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index?id=1" -all
python3 javaEeAccessControlCheck.py "http://127.0.0.1/admin/index" -data-json '{"id":1}' -all
```

## [GET]自动判断/Automatic judgment
![image](https://user-images.githubusercontent.com/40931609/145939989-3e012d69-3884-41ff-9545-970df4564207.png)

## [GET]所有Payload长度/All Response Length
![image](https://user-images.githubusercontent.com/40931609/145940126-278a3c2c-017a-4b2c-935b-763e26ffa03d.png)

## [POST]自动判断/Automatic judgment
![image](https://user-images.githubusercontent.com/40931609/145940164-8b2d828c-106e-43c9-9655-a4be9c617ed6.png)

## [POST]所有Payload长度/All Response Length
![image](https://user-images.githubusercontent.com/40931609/145940303-91b930b9-ca60-4b14-9ea0-fc67f6fe967e.png)

## [POST-JSON]所有Payload长度/All Response Length
![image](https://user-images.githubusercontent.com/40931609/145940402-073befea-188e-4fb1-a2f0-6f055255c48d.png)

# 测试某开源系统
![image](https://user-images.githubusercontent.com/40931609/145940824-51b28b53-fa70-44a5-a891-4565222bef30.png)

可根据不同payload的返回包长度来判断哪些payload可用
![image](https://user-images.githubusercontent.com/40931609/145945707-cd44e164-7c70-40ed-9e35-e70a5a21b376.png)


# 测试某开源系统
![image](https://user-images.githubusercontent.com/40931609/145946705-c8eb8d84-7d25-4dd6-ab31-1e36370e7a65.png)


![image](https://user-images.githubusercontent.com/40931609/145946535-b2948fe3-4b2e-41ce-8d75-c0df8a2d3783.png)

![image](https://user-images.githubusercontent.com/40931609/145946524-1ad02c99-dfba-4af2-a376-72a452f8c722.png)
