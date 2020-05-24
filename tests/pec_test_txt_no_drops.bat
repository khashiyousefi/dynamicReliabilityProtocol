@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 2 -f ./test-files/test.txt -l 1
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o pec_test_txt_no_drops_output.txt

:END
