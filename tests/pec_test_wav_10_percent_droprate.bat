@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 2 -f ./test-files/test.wav -d 10 -b 16
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o pec_test_wav_10_percent_droprate_output.wav

:END
