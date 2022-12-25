import pytest
import sensorlib
from threading import Thread, Lock
from socket import *
import subprocess
import time
import re

from sensor_data import *
 

class TestSensor:
    returned_state: ExpectedStatus = None
    
    def set_returned_state(self, rec_value: int) -> None:
        print(f'stateIN:{self.returned_state}')
        self.returned_state = ExpectedStatus(rec_value)

        #'''Sets the permitted and failed statuses of submitted job for particular test'''
        #if rec_value >= -2 and rec_value < 4:
        #    self.returned_state = ExpectedStatus.STATE_OK
        #elif rec_value < 7:
        #    self.returned_state = ExpectedStatus.STATE_WARNING
        #elif rec_value < 11:
        #    self.returned_state = ExpectedStatus.STATE_ERROR
        #print(f'stateOut:{self.returned_state}')

    @staticmethod
    def parser(out_buf:bytes) -> int:
        try:
            ind = out_buf.rfind(b'"state":')
            assert(ind >= 0)
            return int(chr(out_buf[ind + 9]))
        except Exception as e:
            raise AssertionError(e)


    @staticmethod
    def killer(proc:subprocess, lock_start:Lock, lock_end:Lock) -> None:
        lock_start.release()

        lock_end.acquire(blocking=True, timeout=-1)
        lock_end.release()
        
        time.sleep(2)
        proc.terminate()
        proc.kill()

    def listener(self, lock_start:Lock, lock_end:Lock) -> None:
        """
        A function that can be used by a thread
        """
        # print(threading.currentThread().getName() + '\n')
        proc = subprocess.Popen(
        ['nc', '-l', '3333'],
        stderr=subprocess.STDOUT,  # Merge stdout and stderr
        stdout=subprocess.PIPE)

        kill_thread = Thread(target=self.killer, args=[proc, lock_start, lock_end])
        kill_thread.start()

        (stdoutdata, stderrdata) = proc.communicate(timeout=60)

        print(stdoutdata)
        self.set_returned_state(self.parser(stdoutdata))
        print(f'state:{self.returned_state}')

    def process_transition(self, client_socket:socket, sensor_entry:SensorIdEntry, transition, *args) -> None:

        print('before transition')
        transition(*args)
        print('after transition')

        data = client_socket.recv(1024)
        self.set_returned_state(self.parser(data))

        assert(self.returned_state == sensor_entry.expected_result)
        

    @pytest.mark.parametrize('sensor_entry', sensor_data)
    def test_sensor(self, sensor_entry: SensorIdEntry, test_config: TestConfig) -> None:
        #print(f'test entries: {sensor_entries}')
        #server_socket = socket(AF_INET, SOCK_STREAM)
        #server_socket.bind(("127.0.0.1", 3333));
        #server_socket.listen()

        #print('before lib init')
        # self.process_transition(sensor_init_data[0], sensorlib.StateReporter_init, module, app)
        # sensorlib.StateReporter_init(module, app)
        #print('after lib init')

        #time.sleep(0.1)
        #(client_socket, client_addr) = test_config.server_socket.accept()
        #print('after socket accept')
        #print(sensor_entry)
        sensorlib.StateReporter_set_value(sensor_entry.val, sensor_entry.func_name, sensor_entry.desc)    

        #self.process_transition(client_socket,
        #                        sensor_entry, 
        #                        sensorlib.StateReporter_set_value, 
        #                        bytes(str(sensor_entry.val), encoding = 'utf-8'), 
        #                        sensor_entry.val,
        #                        sensor_entry.func_name, sensor_entry.desc)

        data = test_config.client_socket.recv(1024)
        print(data)
        self.set_returned_state(self.parser(data))

        assert(self.returned_state == sensor_entry.expected_result)

        #sensorlib.StateReporter_stop()
        #client_socket.close()
        #server_socket.close()





        



