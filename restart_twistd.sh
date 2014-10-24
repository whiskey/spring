#!/bin/sh

if [ -f twistd.pid ]; then
    kill -TERM $(cat twistd.pid)
fi
twistd -r kqueue web --class=pyapns.server.APNSServer --port=7077
