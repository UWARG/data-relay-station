import struct


command_types = {
    'debug':        {'cmd':0,   'type':None}, # Print to debug UART
    'set_rollGain': {'cmd':1,   'type':'f'},
    'set_yawGain':  {'cmd':2,   'type':'f'},
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
