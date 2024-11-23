#!/bin/sh

while true;
do
    cd /Users/jun/calendar
    ./get48h.py list > event.txt
    echo '**********'
    cat event.txt
    # ~jun/voicevox/tts.sh 13 event.txt
    ~jun/voicevox/tts.sh 3 event.txt
    sleep 900
done

