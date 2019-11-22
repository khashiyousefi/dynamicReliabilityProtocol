@ ECHO off
CALL :AsyncStartServer
TIMEOUT 1
GOTO :StartClient

:AsyncStartServer
	ECHO "starting server"
	start /b python ../serverDRP.py -r 3 -f ./test-files/high.txt -l ./test-files/low.txt -b 1 -d 25
GOTO :END

:StartClient
	ECHO "starting client"
	python ../clientDRP.py -o fec_test_txt_25_percent_droprate_output.txt

:END
