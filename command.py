### command.py

import struct


command_types = {
    'debug':                    {'cmd':0,   'type':None}, # Print to debug UART
    'set_pitchKDGain':          {'cmd':1,   'type':'f'},
    'set_rollKDGain':           {'cmd':2,   'type':'f'},
    'set_yawKDGain':            {'cmd':3,   'type':'f'},
    'set_pitchKPGain':          {'cmd':4,   'type':'f'},
    'set_rollKPGain':           {'cmd':5,   'type':'f'},
    'set_yawKPGain':            {'cmd':6,   'type':'f'},
    'set_pitchKIGain':          {'cmd':7,   'type':'f'},
    'set_rollKIGain':           {'cmd':8,   'type':'f'},
    'set_yawKIGain':            {'cmd':9,   'type':'f'},
    'set_headingKDGain':        {'cmd':10,  'type':'f'},
    'set_headingKPGain':        {'cmd':11,  'type':'f'},
    'set_headingKIGain':        {'cmd':12,  'type':'f'},
    'set_altitudeKDGain':       {'cmd':13,  'type':'f'},
    'set_altitudeKPGain':       {'cmd':14,  'type':'f'},
    'set_altitudeKIGain':       {'cmd':15,  'type':'f'},
    'set_throttleKDGain':       {'cmd':16,  'type':'f'},
    'set_throttleKPGain':       {'cmd':17,  'type':'f'},
    'set_throttleKIGain':       {'cmd':18,  'type':'f'},
    'set_pathGain':             {'cmd':19,  'type':'f'},
    'set_orbitGain':            {'cmd':20,  'type':'f'},
    'set_showGain':             {'cmd':21,  'type':'B'},
    'set_pitchRate':            {'cmd':22,  'type':'h'},
    'set_rollRate':             {'cmd':23,  'type':'h'},
    'set_yawRate':              {'cmd':24,  'type':'h'},
    'set_pitchAngle':           {'cmd':25,  'type':'h'},
    'set_rollAngle':            {'cmd':26,  'type':'h'},
    'set_yawAngle':             {'cmd':27,  'type':'h'},
    'set_altitude':             {'cmd':28,  'type':'h'},
    'set_heading':              {'cmd':29,  'type':'h'},
    'set_throttle':             {'cmd':30,  'type':'h'},
    'set_autonomousLevel':      {'cmd':31,  'type':'h'},
    'set_angularWalkVariance':  {'cmd':32,  'type':'f'},
    'set_gyroVariance':         {'cmd':33,  'type':'f'},
    'set_magneticVariance':     {'cmd':34,  'type':'f'},
    'set_accelVariance':        {'cmd':35,  'type':'f'},
    'set_scaleFactor':          {'cmd':36,  'type':'f'},
    'calibrate_altimeter':      {'cmd':37,  'type':'f'},
    'clear_waypoints':          {'cmd':38,  'type':'B'},
    'remove_waypoint':          {'cmd':39,  'type':'B'},
    'set_targetWaypoint':       {'cmd':40,  'type':'B'},
    'return_home':              {'cmd':41,  'type':'B'},
    'cancel_returnHome':        {'cmd':42,  'type':'B'},
    'send_heartbeat':           {'cmd':43,  'type':'B'},
    'trigger_camera':           {'cmd':44,  'type':'h'},
    'set_triggerDistance':      {'cmd':45,  'type':'f'},
    'set_gimbleOffset':         {'cmd':46,  'type':'h'},
    'kill_plane':               {'cmd':47,  'type':'h'},
    'unkill_plane':             {'cmd':48,  'type':'h'},
    'lock_goPro':               {'cmd':49,  'type':'h'},
    'arm_vehicle':              {'cmd':50,  'type':'h'},
    'dearm_vehicle':            {'cmd':51,  'type':'h'},
    'set_flap':                 {'cmd':52,  'type':'h'},
    'set_flapKDGain':           {'cmd':53,  'type':'f'},
    'set_flapKPGain':           {'cmd':54,  'type':'f'},
    'set_flapKIGain':           {'cmd':55,  'type':'f'},
    'drop_probe':    	        {'cmd':56,  'type':'B'},
    'reset_probe':		{'cmd':57,  'type':'B'},
    'follow_path':              {'cmd':58,  'type':'B'},
}

multipart_command_types = {
    'new_waypoint':             {'cmd':128, 'type':'ddff'},
    'insert_waypoint':          {'cmd':129, 'type':'ddffBB'},
    'set_returnHomeCoordinates':{'cmd':130, 'type':'ddf'},
    'tare_IMU':                 {'cmd':131,  'type':'fff'},
    'set_IMU':                  {'cmd':132,  'type':'fff'},
    'set_KDValues':              {'cmd':133,  'type':'fffffff'},
    'set_KPValues':              {'cmd':134,  'type':'fffffff'},
    'set_KIValues':              {'cmd':135,  'type':'fffffff'},
    'update_waypoint':          {'cmd':136, 'type':'ddff'},
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
            part_list = values.split(',')
            realval_list = [eval(i) for i in part_list]

            compiled_cmd = bytearray(
                    [multipart_command_types.get(cmd_type).get('cmd')])

            compiled_cmd += struct.pack(
                    multipart_command_types.get(cmd_type).get('type'),
                    *realval_list)

            print("multipart command bytes")
            print(",".join("{}".format(hex(c)) for c in compiled_cmd))
            return True, compiled_cmd

        elif cmd_type in command_types:
            compiled_cmd = bytearray(
                    [command_types.get(cmd_type).get('cmd')])
            if cmd_type == 'debug':                 #printing special case
                compiled_cmd += bytearray(values)
            else:
                realval = eval(values) # THIS IS REALLY BAD, DON'T DO THIS
                print realval
                compiled_cmd += struct.pack(command_types.get(cmd_type).get('type'), realval)
                print ":".join("{}".format(hex(c)) for c in compiled_cmd)

            return True, compiled_cmd
        return False, None
