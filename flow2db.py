import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cityflow.settings")
import django
django.setup()

from metro.models import MetroStation
import argparse
import numpy as np
import json
import datetime


def main(args):
    if args.recreate:
        MetroStation.objects.all().delete()

    n_sample_oneday = int(16.5 * 60 / 10 - 22 - 2)  # =75
    begin = 0 * n_sample_oneday
    end = 9 * n_sample_oneday
    outflow_truth = np.load(args.outflow_truth_path)[begin:end]
    outflow_pred = np.load(args.outflow_pred_path)[begin:end]
    inflow_truth = np.load(args.inflow_path)
    with open('metro/data/station.json') as f:
        station_names = json.load(f)
    # station id, name, datetime, inflow, outflow
    T, N = outflow_truth.shape
    data_list = []
    start = datetime.datetime(2017, 6, 22, 6, 30, 0)
    for t in range(T):
        day = t // n_sample_oneday
        minu = (t % n_sample_oneday + 22) * 10
        timestamp = start + datetime.timedelta(days=day) + datetime.timedelta(minutes=minu)
        for n in range(N):
            data = MetroStation(station_id=n, station_name=station_names[n], inflow=inflow_truth[t, n],
                                outflow=outflow_truth[t, n], outflow_pred=outflow_pred[t, n],
                                timestamp=timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            data_list.append(data)
    MetroStation.objects.bulk_create(data_list)
    print("finish!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw prediction')
    parser.add_argument('--recreate', action='store_true')
    parser.add_argument('--inflow_path', type=str, default='metro/data/inflow_10.npy')
    parser.add_argument('--outflow_truth_path', type=str, default='metro/data/truth_10.npy')
    parser.add_argument('--outflow_pred_path', type=str, default='metro/data/pred_10.npy')
    args = parser.parse_args()

    main(args)
