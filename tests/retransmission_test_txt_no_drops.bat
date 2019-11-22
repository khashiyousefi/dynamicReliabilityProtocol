@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 1 -f ./test-files/test.txt
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o retransmission_test_txt_no_drops_output.txt

:END
