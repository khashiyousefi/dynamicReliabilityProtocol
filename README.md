# Dynamic Reliability Protocol

## Description
This project includes 3 levels of reliability added onto UDP. The intention of this is to ensure that different file formats or differing requirements are met for specific file formats or time restrictions. We intended on providing these 3 reliabilitys to mimic similar reliabilities in protocols such as TCP or RTP, in which we implemented different ways a file could be maintained over an unpredictable protocol such as UDP.
> Note: this program has been tested to work with both ascii and binary file formats as we intended for this to be a robust program; however, the main file formats we used in our testing which are known to work are .txt and .wav

## Running the Program
To run the program you must first start the server to allow it to wait for a request. Then you can start up the client who will make the request and then wait for data to be sent to them.
### Start the server:
```
python serverDRP.py
```
We have included a few optional arguments you can pass in order to control the server's behaviour:
```
python serverDRP.py -i <server ip address>
python serverDRP.py -p <server port>
python serverDRP.py -f <path of file to send>
python serverDRP.py -l <path of lower quality file to send {used only when reliability type is set to FEC>
python serverDRP.py -r <reliability type {RETRANSMISSION=1, PEC=2, FEC=3}>
```

### Start the client:
```
python clientDRP.py
```
We have included a few optional arguments you can pass in order to control the client's behaviour:
```
python serverDRP.py -i <server ip address>
python serverDRP.py -p <server port>
python serverDRP.py -o <name of file to save>
```

## Reliabilities
### Retransmission <r = 1>
This reliability allows the connection to behave similarly to TCP, in which the server will send a data packet, then the client will send an acknowledgement. The main difference is we do not provide flow control, or congestion control. These features could be implemented if the user prefered this behaviour; however, it would be more efficient to just use a TCP connection at that point.
### PEC: Post-Error Correction <r = 2>
Similar to the previous reliability, we will retransmit missing packets; however, this reliability scheme does not use acknowledgements to tell the server the client has received a packet. Instead, we allow the server to transmit the entire file/data, and then the client will respond with a bitmap of all the missing data packets. The server will then start over, but only sending the packets missing, indicated by the bitmap. By default, this behaviour will allow for 3 retranissmission attempts; however, you can change this setting when starting the server.
### FEC: Forward-Error Correction <r = 3>
Instead of performing the error correction after the entire transmission of the data, this reliability scheme allows the client to handle the reliability. RTP contains a similar method of FEC in which it will send packets containing both high quality and lower quality data. The lower quality data will come from the previous packet's higher quality data. If the client is missing a packet, they will retreive the lower quality data from the adjacent packet to ensure no lag occurs and does not require them to request a retransmission.
> Note: This reliability requires the server to include 2 versions of the same file
```
python serverDRP.py -f <high quality file> -l <low quality file>
```