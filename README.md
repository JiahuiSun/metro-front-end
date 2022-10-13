# 地铁出站流量预测、车辆感知调度演示Demo

### 环境

Django

### 运行

- 数据载入
```
python manage.py migrate
python flow2db.py
python road2db.py
```

- 运行
```
python manage.py runserver
```