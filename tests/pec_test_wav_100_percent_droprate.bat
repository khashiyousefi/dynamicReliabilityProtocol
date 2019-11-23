@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 2 -f ./test-files/test.wav -d 100 -b 16 -l 1
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o pec_test_wav_100_percent_droprate_output.wav

:END
