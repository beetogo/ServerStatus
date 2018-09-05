from copy import deepcopy

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

import app_config
import app_tool

app = Flask(__name__)
app.config['SECRET_KEY'] = app_config.SECRET_KEY
socketio = SocketIO(app)

app.logger.info('ServerStatus - Powered by @FanHuaCloud')
app.logger.info('Versions : %s' % app_config.VERSION)


@app.route('/', methods=['GET'])
def index():
    if app_tool.checkMobile(request):
        return render_template('app.html', interval=app_config.INTERVAL)
    else:
        return render_template('index.html', interval=app_config.INTERVAL)




@app.route('/push', methods=['GET'])
def push():
    return render_template('push.html')


@socketio.on('connect', namespace='/info')
def socketio_connect():
    app.logger.info('Client connected.Client SID：%s' % request.sid)


@socketio.on('disconnect', namespace='/info')
def socketio_disconnect():
    app.logger.info('Client disconnected.Client SID：%s' % request.sid)


@socketio.on('info_update', namespace='/info')
def info_update():
    send_data = deepcopy(app_config.SERVER_INFO)
    for value in send_data.values():
        del value['token']

    emit('info_update', send_data)


@socketio.on('server_push', namespace='/info')
def server_push(data):
    # 定义服务器上来的数据
    data_name = ['uuid', 'cpu_precent', 'memory', 'memory_all', 'update_time', 'uptime', 'load',
                 'network_in', 'network_out', 'traffic_in', 'traffic_out', 'hdd', 'hdd_all', 'token']

    # 判断数据是否完全
    for info in data:
        if info not in data_name:
            return emit('server_push', {'status': False, 'msg': 'Data not correct'})

    # 判断UUID与TOKEN
    uuid = data['uuid']
    if uuid not in app_config.SERVER_INFO:
        return emit('server_push', {'status': False, 'msg': 'Server uuid not found'})

    if app_config.SERVER_INFO[uuid]['token'] != data['token']:
        return emit('server_push', {'status': False, 'msg': 'Server token is not correct'})

    """
            {'name': '测试', 'cpu_precent': 0, 'memory': 0, 'memory_all': 0, 'update_time': 0, 'uptime': 0, 'load': 0,
             'network_in': 0, 'network_out': 0, 'traffic_in': 0, 'traffic_out': 0, 'hdd': 0, 'hdd_all': 0,
             'token': '123456'},
    """

    # 写入数据
    app_config.SERVER_INFO[uuid]['cpu_precent'] = float(data['cpu_precent'])
    app_config.SERVER_INFO[uuid]['memory'] = float(data['memory'])
    app_config.SERVER_INFO[uuid]['memory_all'] = float(data['memory_all'])
    app_config.SERVER_INFO[uuid]['update_time'] = float(data['update_time'])
    app_config.SERVER_INFO[uuid]['uptime'] = float(data['uptime'])
    app_config.SERVER_INFO[uuid]['load'] = data['load']
    app_config.SERVER_INFO[uuid]['network_in'] = float(data['network_in'])
    app_config.SERVER_INFO[uuid]['network_out'] = float(data['network_out'])
    app_config.SERVER_INFO[uuid]['traffic_in'] = float(data['traffic_in'])
    app_config.SERVER_INFO[uuid]['traffic_out'] = float(data['traffic_out'])
    app_config.SERVER_INFO[uuid]['hdd'] = float(data['hdd'])
    app_config.SERVER_INFO[uuid]['hdd_all'] = float(data['hdd_all'])
    #app_config.SERVER_INFO[uuid]['last_update'] = time.time()

    # 返回
    return emit('server_push', {'status': True, 'msg': 'Push data success'})
