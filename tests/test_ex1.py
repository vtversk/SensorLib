import pytest
import sensorlib
from dataclasses import dataclass, asdict
from threading import Thread, Lock
from socket import *
import subprocess
import time
import re
import json

from sensor_data import ExpectedStatus, sensor_data, sensor_multiple_data, SensorIdEntry, TestConfig 
 

class TestSensor:
    @staticmethod
    def parse_multiple_messages(data: bytes) -> list:
        mes_list = []
        out_str = data.decode('utf-8', errors='ignore')
        while out_str != '':
            try:
                indl = out_str.find('{')
                indr = out_str.find('}') + 1
                mes_str = out_str[indl:indr]
                out_str = out_str[indr:]
                rec_mes = json.loads(mes_str)
                rec_mes['state'] = ExpectedStatus(int(rec_mes['state']))
                mes_list.append(rec_mes)
            except:
                break
        return mes_list



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

    @pytest.mark.parametrize('sensor_entry', sensor_multiple_data)
    def test_sensor_multiple_messages(self, sensor_entry:list, test_config: TestConfig) -> None:
        nMessages = len(sensor_entry)
        assert ( nMessages == 4)
        check_func_names = ('func1', 'func2', 'func3', 'func4')
        expected_list=[]
        for message in sensor_entry:
            assert message.message_fields.func in check_func_names
            dict_config_fields = asdict(test_config.message_fields)
            dict_transmit_fields = asdict(message.message_fields)
            expected_message = {**dict_config_fields,**dict_transmit_fields}
            expected_message['state'] = message.expected_result  
            expected_list.append(expected_message)          
            sensorlib.StateReporter_set_value(message.val, message.message_fields.func.encode('utf-8'), 
                                              message.message_fields.desc.encode('utf-8'))
    
        data = test_config.client_socket.recv(1024)
        rec_mes = self.parse_multiple_messages(data)
        assert len(rec_mes) == nMessages

        for ind, exp_mes in enumerate(expected_list):
            assert (exp_mes == rec_mes[ind])
