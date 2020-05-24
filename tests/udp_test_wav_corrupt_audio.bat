@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 0 -f ./test-files/test.wav -d 25 -l 1
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o udp_test_wav_corrupt_audio.wav

:END
