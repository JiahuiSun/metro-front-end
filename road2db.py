import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cityflow.settings")
import django
django.setup()
from metro.models import RoadYX
import argparse
import datetime
import pickle


def main(args):
    if args.recreate:
        RoadYX.objects.all().delete()

    start = datetime.datetime(2017, 6, 1, 10, 0, 0)
    data_list = []
    with open(args.sensing_path, 'rb') as f:
        road_list = pickle.load(f)
    for road in road_list:
        timestamp = start + datetime.timedelta(hours=road['timestamp'])
        data = RoadYX(task='sensing', algo=road['algo'],
                      timestamp=timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                      color=road['color'], shape=road['shape'])
        data_list.append(data)

    with open(args.order_path, 'rb') as f:
        road_list = pickle.load(f)
    for road in road_list:
        timestamp = start + datetime.timedelta(hours=road['timestamp'])
        data = RoadYX(task='order', algo=road['algo'],
                      timestamp=timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                      color=road['color'], shape=road['shape'])
        data_list.append(data)
    RoadYX.objects.bulk_create(data_list)
    print("finish!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw prediction')
    parser.add_argument('--recreate', action='store_true')
    parser.add_argument('--sensing_path', type=str, default='metro/data/sensing_data_yx.pkl')
    parser.add_argument('--order_path', type=str, default='metro/data/order_data_yx.pkl')
    args = parser.parse_args()

    main(args)
