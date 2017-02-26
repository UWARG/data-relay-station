from data_relay import DataRelay

def signal_handler(*args):
    print("Killed by user")
    # teardown()
    sys.exit(0)

def main(simfile, simspeed):

    #initialize UDP connections
    #TODO

    #start data relay
    relay = DataRelay(simfile, simspeed)

    #start multi echo
    #TODO

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Read data from xbee, write it locally and replay it over the network to connected clients.")
    parser.add_argument("--simfile", metavar="FILE", required=False, help="list of files (separated by commas) to simulate incoming plane data")
    parser.add_argument("--simspeed", metavar="NUMBER", required=False, help="speed to play the simfile at in seconds per frame")
    args = parser.parse_args()
    #Default Sim Speed
    simspeed = 0.2
    if (args.simspeed):
        simspeed = float(args.simspeed)
    simfile= ''
    if(args.simfile):
        simfile = args.simfile

    main(simfile, simspeed)
