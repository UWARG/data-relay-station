from data_relay import DataRelay


def main(simfile, simspeed):
    relay = DataRelay(simfile, simspeed)
    #initialize UDP connections
    #start data relay
    #start multi echo

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Read data from xbee, write it locally and replay it over the network to connected clients.")
    parser.add_argument("--simfile", metavar="FILE", required=False, help="list of files (separated by commas) to simulate incoming plane data")
    parser.add_argument("--simspeed", metavar="NUMBER", required=False, help="speed to play the simfile at in seconds per frame")
    parser.add_argument("--log", action='store_true', help="Always write log file (even in simulator mode).")
    parser.add_argument("--nolog", action='store_true', help="Never write log file.")
    args = parser.parse_args()
    #Default Sim Speed
    simspeed = 0.2
    if (args.simspeed):
        simspeed = float(args.simspeed)
    simfile= ''
    if(args.simfile):
        simfile = args.simfile

    main(simfile, simspeed)
