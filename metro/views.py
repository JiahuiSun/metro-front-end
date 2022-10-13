from django.shortcuts import render
import numpy as np
import json
from datetime import datetime, timedelta
from metro.models import MetroStation, RoadYX


def out_of_range(timestamp):
    day_st = datetime(2017, 6, 22, 0, 0, 0)
    day_end = datetime(2017, 6, 30, 23, 59, 59)
    if timestamp < day_st or timestamp > day_end:
        return True
    minu_st = datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day, hour=10, minute=10, second=0)
    minu_end = datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day, hour=22, minute=30, second=0)
    if timestamp < minu_st or timestamp > minu_end:
        return True
    return False


def index(request):
    if 'page_date' in request.POST:
        cur_time = request.POST['page_date'] + ' ' + request.POST['page_time']
        if out_of_range(datetime.strptime(cur_time, '%Y-%m-%d %H:%M:%S')):
            cur_time = '2017-06-22 10:10:00'
    else:
        cur_time = '2017-06-22 10:10:00'

    next_time = datetime.strptime(cur_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=10)
    if out_of_range(next_time):
        next_time = cur_time
    else:
        next_time = next_time.strftime('%Y-%m-%d %H:%M:%S')
    cur_datas = MetroStation.objects.filter(timestamp=cur_time)
    next_datas = MetroStation.objects.filter(timestamp=next_time)
    # 当前时刻所有站点的出入站流量和下一时刻出站流量，{'深圳北站': {'station_name': '深圳北站'，'inflow': 20}}
    station_info = dict()
    for data in cur_datas:
        station_info[data.station_name] = dict()
        station_info[data.station_name]['station_name'] = data.station_name
        station_info[data.station_name]['inflow'] = data.inflow
        station_info[data.station_name]['outflow'] = data.outflow
    for data in next_datas:
        station_info[data.station_name]['outflow_pred'] = data.outflow_pred
        station_info[data.station_name]['outflow_truth'] = data.outflow

    if 'station_name' in request.POST:
        station_name = request.POST['station_name']
    else:
        station_name = '南山'
    # 一周每天的流量
    start_time = '2017-06-23 10:10:00'
    end_time = '2017-06-29 22:30:00'
    query = f"SELECT * FROM metro_metrostation "\
            f"WHERE `station_name` = '{station_name}' "\
            f"AND `timestamp` >= '{start_time}' "\
            f"AND `timestamp` <= '{end_time}' "\
            f"ORDER BY `timestamp`"
    flow_week = MetroStation.objects.raw(query)
    station_flow_week = dict()
    station_flow_week['inflow'] = [flow.inflow for flow in flow_week]
    station_flow_week['outflow'] = [flow.outflow for flow in flow_week]
    station_flow_week['outflow_pred'] = [flow.outflow_pred for flow in flow_week]

    # 一周平均的流量
    station_flow_avg = dict()
    station_flow_avg['inflow'] = \
        np.mean(np.array(station_flow_week['inflow']).reshape(7, -1), axis=0).astype(np.int).tolist()
    station_flow_avg['outflow'] = \
        np.mean(np.array(station_flow_week['outflow']).reshape(7, -1), axis=0).astype(np.int).tolist()
    station_flow_avg['outflow_pred'] = \
        np.mean(np.array(station_flow_week['outflow_pred']).reshape(7, -1), axis=0).astype(np.int).tolist()
    station_flow_avg['x'] = np.arange(len(station_flow_avg['inflow'])).astype(np.int).tolist()
    st = datetime(year=2017, month=6, day=22, hour=10, minute=10, second=0)
    end = datetime(year=2017, month=6, day=22, hour=22, minute=30, second=0)
    xaxis = []
    while st <= end:
        xaxis.append(st.strftime('%H:%M'))
        st += timedelta(minutes=10)
    station_flow_avg['x'] = xaxis
    station_flow_week['x'] = station_flow_avg['x'] * 7

    # 给定站点今天初始到当前时间的出入站流量
    start_time = cur_time[:10] + ' 10:10:00'
    query = f"SELECT * FROM metro_metrostation "\
            f"WHERE `station_name` = '{station_name}' "\
            f"AND `timestamp` >= '{start_time}' "\
            f"AND `timestamp` <= '{cur_time}' "\
            f"ORDER BY `timestamp`"
    flow_today = MetroStation.objects.raw(query)
    station_flow_today = dict()
    station_flow_today['inflow'] = [flow.inflow for flow in flow_today]
    station_flow_today['outflow'] = [flow.outflow for flow in flow_today]
    station_flow_today['outflow_pred'] = [flow.outflow_pred for flow in flow_today]
    station_flow_today['x'] = station_flow_avg['x']

    return render(request, 'metro/index.html',
                  {'page_date': cur_time[:10], 'page_time': cur_time[11:], 'station_name': station_name,
                   'station_info': station_info, 'station_flow_today': json.dumps(station_flow_today),
                   'station_flow_week': json.dumps(station_flow_week),
                   'station_flow_avg': json.dumps(station_flow_avg)})


def sensing(request):
    if 'page_date' in request.POST:
        timestamp = request.POST['page_date'] + ' ' + request.POST['page_time']
    else:
        timestamp = '2017-06-01 11:00:00'

    # sensing_ours
    sensing_ours = dict()
    task = 'sensing'
    algo = 'WLU'
    query = f"SELECT * FROM metro_roadyx "\
            f"WHERE `task` = '{task}' "\
            f"AND `algo` = '{algo}' "\
            f"AND `timestamp` = '{timestamp}'"
    road_data = RoadYX.objects.raw(query)
    for road in road_data:
        sensing_ours[road.id] = dict()
        sensing_ours[road.id]['color'] = road.color
        sensing_ours[road.id]['shape'] = road.shape

    # sensing_baseline
    sensing_baseline = dict()
    task = 'sensing'
    algo = 'CV'
    query = f"SELECT * FROM metro_roadyx "\
            f"WHERE `task` = '{task}' "\
            f"AND `algo` = '{algo}' "\
            f"AND `timestamp` = '{timestamp}'"
    road_data = RoadYX.objects.raw(query)
    for road in road_data:
        sensing_baseline[road.id] = dict()
        sensing_baseline[road.id]['color'] = road.color
        sensing_baseline[road.id]['shape'] = road.shape

    # order_ours
    order_ours = dict()
    task = 'order'
    algo = 'WLU'
    query = f"SELECT * FROM metro_roadyx "\
            f"WHERE `task` = '{task}' "\
            f"AND `algo` = '{algo}' "\
            f"AND `timestamp` = '{timestamp}'"
    road_data = RoadYX.objects.raw(query)
    for road in road_data:
        order_ours[road.id] = dict()
        order_ours[road.id]['color'] = road.color
        order_ours[road.id]['shape'] = road.shape

    # order_baseline
    order_baseline = dict()
    task = 'sensing'
    algo = 'CV'
    query = f"SELECT * FROM metro_roadyx "\
            f"WHERE `task` = '{task}' "\
            f"AND `algo` = '{algo}' "\
            f"AND `timestamp` = '{timestamp}'"
    road_data = RoadYX.objects.raw(query)
    for road in road_data:
        order_baseline[road.id] = dict()
        order_baseline[road.id]['color'] = road.color
        order_baseline[road.id]['shape'] = road.shape

    return render(request, 'metro/sensing.html',
                  {'sensing_ours': sensing_ours, 'sensing_baseline': sensing_baseline,
                   'order_ours': order_ours, 'order_baseline': order_baseline,
                   'page_date': timestamp[:10], 'page_time': timestamp[11:]})
