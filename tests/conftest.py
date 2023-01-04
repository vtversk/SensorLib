import pytest
import sensorlib
from dataclasses import dataclass
from socket import *
from sensor_data import TestConfig, ConfigTimeFields

module = 'module1'
app = 'block1'


@pytest.fixture(scope='session', name='test_config')
def sensor_config() -> TestConfig:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 3333));
    server_socket.listen()

    sensorlib.StateReporter_init(module.encode('utf-8'), app.encode('utf-8'))
    (client_socket, client_addr) = server_socket.accept()
    yield TestConfig(client_socket, ConfigTimeFields(module, app))

    sensorlib.StateReporter_stop()
    client_socket.close()
    server_socket.close()
