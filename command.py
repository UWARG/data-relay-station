import struct


command_types = {
    'debug':        {'cmd':0,   'type':None}, # Print to debug UART
    'set_pitchKDGain': {'cmd':1,   'type':'f'},
    'set_rollKDGain':  {'cmd':2,   'type':'f'},
    'set_yawKDGain':  {'cmd':3,   'type':'f'},
    'set_pitchKPGain':  {'cmd':4,   'type':'f'},
    'set_rollKPGain':  {'cmd':5,   'type':'f'},
    'set_yawKPGain':  {'cmd':6,   'type':'f'},
    'set_pitchKIGain':  {'cmd':7,   'type':'f'},
    'set_rollKIGain':  {'cmd':8,   'type':'f'},
    'set_yawKIGain':  {'cmd':9,   'type':'f'},
    'set_headingKDGain':  {'cmd':10,   'type':'f'},
    'set_headingKPGain':  {'cmd':11,   'type':'f'},
    'set_headingKIGain':  {'cmd':12,   'type':'f'},
    'set_altitudeKDGain':  {'cmd':13,   'type':'f'},
    'set_altitudeKPGain':  {'cmd':14,   'type':'f'},
    'set_altitudeKIGain':  {'cmd':15,   'type':'f'},
    'set_throttleKDGain':  {'cmd':16,   'type':'f'},
    'set_throttleKPGain':  {'cmd':17,   'type':'f'},
    'set_throttleKIGain':  {'cmd':18,   'type':'f'},
    'set_pathGain':  {'cmd':19,   'type':'f'},
    'set_orbitGain':  {'cmd':20,   'type':'f'},
    'set_showGain':  {'cmd':21,   'type':'B'},
    'set_pitchRate':  {'cmd':22,   'type':'h'},
    'set_rollRate':  {'cmd':23,   'type':'h'},
    'set_yawRate':  {'cmd':24,   'type':'h'},
    'set_pitchAngle':  {'cmd':25,   'type':'f'},
    'set_rollAngle':  {'cmd':26,   'type':'f'},
    'set_yawAngle':  {'cmd':27,   'type':'f'},
    'set_altitude':  {'cmd':28,   'type':'f'},
    'set_heading':  {'cmd':29,   'type':'f'},
    'set_throttle':  {'cmd':30,   'type':'f'},
    'tare_IMU':  {'cmd':31,   'type':None},
    'set_autonomousLevel':  {'cmd':32,   'type':'B'},    
}

multipart_command_types = {
    'new_waypoint':128,
}

class CommandParser:

    def __init__(self):
        pass

    def parse_command(self, cmd_str):
        if ':' not in cmd_str:
            return False, None
        cmd_type, values = cmd_str.split(':', 1)
        compiled_cmd = b''
        if cmd_type in multipart_command_types:
            # TODO: handle multipart command
            pass
        elif cmd_type in command_types:
            compiled_cmd = bytearray(
                    [command_types.get(cmd_type).get('cmd')])
            if cmd_type == 'debug':                 #printing special case
                compiled_cmd += bytearray(values)
            else:
                realval = eval(values) # THIS IS REALLY BAD, DON'T DO THIS
                compiled_cmd += struct.pack('f', realval)
            return True, compiled_cmd
        return False, None
