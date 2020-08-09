#!/usr/bin/env python3
from project import app
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        app.run(host=sys.argv[1])
    else:
        app.run()
