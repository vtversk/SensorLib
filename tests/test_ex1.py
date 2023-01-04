import pytest
import sensorlib
from dataclasses import dataclass, asdict
from threading import Thread, Lock
from socket import *
import subprocess
import time
import re
import json

from sensor_data import ExpectedStatus, sensor_data, SensorIdEntry, TestConfig 
 

class TestSensor:
    @pytest.mark.parametrize('sensor_entry', sensor_data)
    def test_sensor(self, sensor_entry: SensorIdEntry, test_config: TestConfig) -> None:
        dict_config_fields = asdict(test_config.message_fields)
        dict_transmit_fields = asdict(sensor_entry.message_fields)
        expected_message = {**dict_config_fields,**dict_transmit_fields}
        expected_message['state'] = sensor_entry.expected_result

        sensorlib.StateReporter_set_value(sensor_entry.val, sensor_entry.message_fields.func.encode('utf-8'), 
                                          sensor_entry.message_fields.desc.encode('utf-8'))  

        time.sleep(1)
        data = test_config.client_socket.recv(1024)

        #temporary take only the last message, since behavior is not clear
        out_str = data.decode('utf-8', errors='ignore')
        ind = out_str.rfind('{')
        out_str = out_str[ind:]
        rec_mes = json.loads(out_str)
        rec_mes['state'] = ExpectedStatus(int(rec_mes['state']))
        assert(rec_mes == expected_message)
