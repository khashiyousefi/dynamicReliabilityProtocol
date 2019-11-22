@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 1 -f ./test-files/test.wav -d 50 -b 16
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o retransmission_test_wav_50_percent_droprate_output.wav

:END
