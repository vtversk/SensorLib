from dataclasses import dataclass
from enum import Enum
from socket import socket

class ExpectedStatus(Enum):
    '''Used to describe sensor status.'''
    STATE_OK = 0
    STATE_WARNING = 1
    STATE_ERROR = 2
    STATE_UNAVAILABLE = 3

@dataclass
class ConfigTimeFields:
    module:str
    app:str

@dataclass
class TestConfig:
    client_socket: socket
    message_fields: ConfigTimeFields

@dataclass 
class TransmitFields:
    func:str
    desc:str

@dataclass
class SensorIdEntry:
    '''Holds one entry of test data.'''
    val: bytes
    message_fields:TransmitFields
    expected_result: ExpectedStatus

sensor_init_data = [SensorIdEntry(-1, TransmitFields('',''),ExpectedStatus.STATE_OK)]

sensor_data = [
        #assuming values outside of specified range return STATE_UNAVAILABLE
        SensorIdEntry(b'-3', TransmitFields('func1', 'max_int_neg_unavail'), ExpectedStatus.STATE_UNAVAILABLE),
        #to check border float value. 0.01 is selected as minimal value, beacuse if greater precision is required
        # it make sense to shift the whole range to 1000 times smaller values 
        SensorIdEntry(b'-2.01', TransmitFields('func2', 'max_float_neg_unavail'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-2', TransmitFields('func1', 'min_int_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-1.99', TransmitFields('func1', 'min_float_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-1', TransmitFields('func1', 'middle_int_neg_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-0.5', TransmitFields('func1', 'middle_float_neg_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-0.01', TransmitFields('func1', 'min_float_neg_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'0', TransmitFields('func1', 'zero'), ExpectedStatus.STATE_OK),
        #change func name in the middle of the range
        SensorIdEntry(b'0.01', TransmitFields('func2', 'min_float_pos_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'1', TransmitFields('func2', 'min_int_pos_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'1.5', TransmitFields('func2', 'middle_float_pos_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'2', TransmitFields('func2', 'middle_int_pos_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'3', TransmitFields('func2', 'max_int_pos_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'3.99', TransmitFields('func2', 'max_float_pos_ok'), ExpectedStatus.STATE_OK),
        SensorIdEntry(b'4', TransmitFields('func2', 'min_int_warn'), ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'4.01', TransmitFields('func2', 'min_float_warn'), ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'5', TransmitFields('func2', 'middle_int_warn'), ExpectedStatus.STATE_WARNING),
        #change func name in the middle of the range
        SensorIdEntry(b'5.5', TransmitFields('func3', 'middle_float_warn'), ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'6', TransmitFields('func3', 'max_int_warn'), ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'6.99', TransmitFields('func3', 'max_float_warn'), ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'7', TransmitFields('func3', 'min_int_error'), ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'7.01', TransmitFields('func3', 'min_float_error'), ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'9', TransmitFields('func3', 'middle_int_error'), ExpectedStatus.STATE_ERROR),
        #change func name in the middle of the range
        SensorIdEntry(b'9.5', TransmitFields('func4', 'middle_float_error'), ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'10', TransmitFields('func4', 'max_int_error'), ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'10.99', TransmitFields('func4', 'max_float_error'), ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'11', TransmitFields('func4', 'min_int_pos_uavail'), ExpectedStatus.STATE_UNAVAILABLE),
        SensorIdEntry(b'11.01', TransmitFields('func4', 'min_float_pos_unavail'), ExpectedStatus.STATE_UNAVAILABLE),
        SensorIdEntry(b'12', TransmitFields('func4', 'int_pos_unavail'), ExpectedStatus.STATE_UNAVAILABLE),
        SensorIdEntry(b'12.5', TransmitFields('func4', 'float_pos_unavail'), ExpectedStatus.STATE_UNAVAILABLE),
]

   

    