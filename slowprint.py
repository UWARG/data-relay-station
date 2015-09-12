### slowprint.py

import time

def main():
    while True:
        print 'a\r\n'
        time.sleep(1)

if __name__ == '__main__':
    main()
