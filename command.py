### command.py

import struct

# For recerence:
# x : null : 1 byte
# B : char : 1 byte
# h : int : 2 bytes
# f : float : 4 bytes
# d : long double : 8 bytes

command_types = {
    'debug':                    {'cmd':0,   'type':None}, # Print to debug UART
    'set_heading_gain':         {'cmd':1,   'type':'f'},
    'set_altitude_gain':        {'cmd':2,   'type':'f'},
    'set_ground_speed_gain':    {'cmd':3,   'type':'f'},
    'show_gains':               {'cmd':4,   'type':'B'},
   
    'set_path_gain':            {'cmd':19,  'type':'f'},
    'set_orbit_gain':           {'cmd':20,  'type':'f'},

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
    'reset_probe':		        {'cmd':57,  'type':'B'},
    'follow_path':              {'cmd':58,  'type':'B'},
    'show_scaled_pwm':          {'cmd':60,  'type':'B'},
}

multipart_command_types = { # append pad bytes so all waypoint commands are the same size
    'new_waypoint':             {'cmd':128, 'type':'ddffB3x'}, # lon, lat, alt, rad, type
    'insert_waypoint':          {'cmd':129, 'type':'ddffxBBx'}, # lon, lat, alt, rad, prev, next
    'set_returnHomeCoordinates':{'cmd':130, 'type':'ddf8x'}, # lon, lat, alt
    'tare_IMU':                 {'cmd':131, 'type':'fff'},
    'set_IMU':                  {'cmd':132, 'type':'fff'},
    
    'update_waypoint':          {'cmd':136, 'type':'ddffBxxB'}, # lon, lat, alt, rad, type, id
    'set_roll_rate_gains':      {'cmd':137, 'type': 'fff'}, #kp, kd, ki
    'set_pitch_rate_gains':     {'cmd':138, 'type': 'fff'},
    'set_yaw_rate_gains':       {'cmd':139, 'type': 'fff'},
    'set_roll_angle_gains':     {'cmd':140, 'type': 'fff'},
    'set_pitch_angle_gains':    {'cmd':141, 'type': 'fff'},
}

class CommandParser:

    def __init__(self):
        pass

    def parse_command(self, cmd_str):
        if ':' not in cmd_str:
            return False, None

        try:
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
        except Exception as e:
            print("Failed to parse command \"{}\" because of error: {}".format(cmd_str, e))

        return False, None
