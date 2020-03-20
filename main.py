import subprocess
import csv
from scipy import stats
from math import log
import datetime
import numpy
from matplotlib.pyplot import show, legend, ylim, plot_date, grid, yticks, gca
from matplotlib.ticker import FuncFormatter
from pprint import pformat
import pickle
import logging


logger = logging.getLogger(__name__)


def log2(num):
    return log(num)/log(2)


jan1 = datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')


PLACES_OF_INTEREST = [
    ('Province/State', 'San Francisco County, CA'),
    ('Province/State', 'British Columbia'),
    ('Province/State', 'California'),
    ('Province/State', 'New York'),
    ('Province/State', 'Washington'),
    ('Province/State', 'Alberta'),
    ('Province/State', 'Ontario')]


def download():
    process = subprocess.Popen(
        ['kaggle', 'datasets', 'download', '--force', '-d', 'sudalairajkumar/novel-corona-virus-2019-dataset'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    mkdirProcess = subprocess.Popen(['mkdir', '-p', 'dataset'])
    tarProcess = subprocess.Popen(['tar', '-C', 'dataset', '-xvf',
                                   'novel-corona-virus-2019-dataset.zip'])
    stdout, stderr = process.communicate()
    logger.info('done downloading')
    pickle.dump(datetime.datetime.now(), open('last_download_date.p', 'wb'))


def download_per_day():
    today = datetime.datetime.now()
    try:
        last_download = pickle.load(open('last_download_date.p', 'rb'))
    except OSError or (today - last_download).day > 0:
        download()


def get_for_region(region_name, data):
    obs = [{
        'date': datetime.datetime.strptime(d['ObservationDate'], '%m/%d/%Y'),
        'confirmed': int(float(d['Confirmed'])),
        'logcount': log2(float(d['Confirmed'])),
        }
        for d in data[region_name]]
    for ob in obs:
        ob['day'] = (ob.get('date') - jan1).days
    return obs


def get_x_y(region_data):
    x = []
    y = []
    for datum in region_data:
        x.append(datum['day'])
        y.append(datum['logcount'])
    return x, y


def read_csv():
    reader = csv.DictReader(open('./dataset/covid_19_data.csv'))
    data = {}
    for row in reader:
        for k, v in PLACES_OF_INTEREST:
            if v == row[k]:
                if not data.get(v):
                    data[v] = []
                data[v].append(row)
    return data


def get_lin_regression(region, data):
    data = get_for_region(region, data)
    x, y = get_x_y(data)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    logger.info(f'Region: {region}, slope: {slope}, intercept {intercept}, r_value {r_value} p_value {p_value} std_err={std_err}')
    return slope, intercept


def plot_region(region, color, label):
    data = read_csv()
    slope, intercept = get_lin_regression(region, data)
    data = get_for_region(region, data)

    x, y = get_x_y(data)
    current_day = (datetime.datetime.now() - jan1).days
    predict_x = [jan1 + datetime.timedelta(days=day) for day in range(current_day, current_day + 200)]
    predict_y = [numpy.power(2, (slope * y) + intercept) for y in range(current_day, current_day + 200)]
    plot_date(
        [jan1 + datetime.timedelta(days=day) for day in x],
        numpy.power(2, y),
        color=color,
        label=label,
        linestyle='solid')
    plot_date(
        predict_x,
        predict_y,
        color=color,
        marker=None,
        linestyle='dotted')
    logger.info(f'Region: {region}')
    logger.info(pformat({'data': list(zip(map(str, predict_x), predict_y))}))


colors = ['blue', 'green', 'brown', 'purple', 'orange', 'pink']


def main():
    regions = ['British Columbia', 'California', 'New York', 'Ontario', 'Washington']
    # regions = ['British Columbia']
    for region in regions:
        plot_region(region, color=colors[regions.index(region)], label=region)

    ylim(0, 2000000)
    grid(color='grey', linestyle='solid', linewidth=1)
    yticks(numpy.arange(0, 2000000, step=250000))
    ax = gca()
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    legend()
    show()


if __name__ == '__main__':
    download_per_day()
    main()
