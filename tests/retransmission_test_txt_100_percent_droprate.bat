@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 1 -f ./test-files/test.txt -d 100 -l 1
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o retransmission_test_txt_100_percent_droprate_output.txt

:END
