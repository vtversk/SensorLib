import pytest
import sensorlib
from socket import *
from sensor_data import TestConfig

module = b'module1'
app = b'block1'


@pytest.fixture(scope='session', name='test_config')
def sensor_config() -> TestConfig:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 3333));
    server_socket.listen()

    sensorlib.StateReporter_init(module, app)
    (client_socket, client_addr) = server_socket.accept()
    yield TestConfig(client_socket)

    sensorlib.StateReporter_stop()
    client_socket.close()
    server_socket.close()
