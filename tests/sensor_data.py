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
class TestConfig:
    client_socket: socket


@dataclass
class SensorIdEntry:
    '''Holds one entry of test data.'''
    val: bytes
    func_name: bytes
    desc: bytes 
    expected_result: ExpectedStatus

sensor_init_data = [SensorIdEntry(-1, b'',b'',ExpectedStatus.STATE_OK)]

sensor_data = [
        #assuming values outside of specified range return STATE_UNAVAILABLE
        SensorIdEntry(b'-3', b'func1', b'max_int_neg_unavail', ExpectedStatus.STATE_UNAVAILABLE),
        #to check border float value. 0.01 is selected as minimal value, beacuse if greater precision is required
        # it make sense to shift the whole range to 1000 times smaller values 
        SensorIdEntry(b'-2.01', b'func1', b'max_float_neg_unavail', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-2', b'func1', b'min_int_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-1.99', b'func1', b'min_float_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-1', b'func1', b'middle_int_neg_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-0.5', b'func1', b'middle_float_neg_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'-0.01', b'func1', b'min_float_neg_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'0', b'func1', b'zero', ExpectedStatus.STATE_OK),
        #change func name in the middle of the range
        SensorIdEntry(b'0.01', b'func2', b'min_float_pos_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'1', b'func2', b'min_int_pos_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'1.5', b'func2', b'middle_float_pos_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'2', b'func2', b'middle_int_pos_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'3', b'func2', b'max_int_pos_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'3.99', b'func2', b'max_float_pos_ok', ExpectedStatus.STATE_OK),
        SensorIdEntry(b'4', b'func2', b'min_int_warn', ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'4.01', b'func2', b'min_float_warn', ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'5', b'func2', b'middle_int_warn', ExpectedStatus.STATE_WARNING),
        #change func name in the middle of the range
        SensorIdEntry(b'5.5', b'func3', b'middle_float_warn', ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'6', b'func3', b'max_int_warn', ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'6.99', b'func3', b'max_float_warn', ExpectedStatus.STATE_WARNING),
        SensorIdEntry(b'7', b'func3', b'min_int_error', ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'7.01', b'func3', b'min_float_error', ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'9', b'func3', b'middle_int_error', ExpectedStatus.STATE_ERROR),
        #change func name in the middle of the range
        SensorIdEntry(b'9.5', b'func4', b'middle_float_error', ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'10', b'func4', b'max_int_error', ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'10.99', b'func4', b'max_float_error', ExpectedStatus.STATE_ERROR),
        SensorIdEntry(b'11', b'func4', b'min_int_pos_uavail', ExpectedStatus.STATE_UNAVAILABLE),
        SensorIdEntry(b'11.01', b'func4', b'min_float_pos_unavail', ExpectedStatus.STATE_UNAVAILABLE),
        SensorIdEntry(b'12', b'func4', b'int_pos_unavail', ExpectedStatus.STATE_UNAVAILABLE),
        SensorIdEntry(b'12.5', b'func4', b'float_pos_unavail', ExpectedStatus.STATE_UNAVAILABLE),
]


    

    