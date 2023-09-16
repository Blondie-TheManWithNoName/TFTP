
# TFTP
TFTP Server and Client implemented with Python 3.5 and a designed GUI with PyQt5.
<br></br>

# Idea
TFTP is a protocol used to transfer files from a Client to a Server, this is a simple protocol and is not used to make complex transfers.

In this TFTP I have used the RFC standards to implement several features of it. Every time a RRQ or WRQ packet is sent together the Client options are sent.  The server responds with an OACK, which has the operation code 6, so we confirm the client's request and start sending DATA and ACKs.

I have also implemented the time out of the Stop & Wait protocol, every time a packet has to be received there is a waiting time called time out that is waited until a message is received, if the time limit is reached it is tried again from the beginning, either sending the ACK or the DATA depending on the situation. You are able to change the time out on the Client Interface depending on the situation.

You can use this TFTP locally on your on network (127.0.0.1) or with other networks with the corresponding IP and with the port 69 open on the network the Server is gonna be used.
<br></br>
<br></br>
## **Client Features**
<br></br>
- Choose server **IP** address
- Choose between doing a **GET** (download) or **PUT** (upload)
- Choose between **Netascii** or **Octet**
- Choose file to download or upload
<br></br>
![image4](https://github.com/Blondie-TheManWithNoName/TFTP/assets/58909117/768b42d2-c5e8-4f39-ad96-d498f19c2092)
<br></br>
- Set size of each package
      - Power of 2
      - Just a natural number
- Set seconds to wait in case of time out
- Port to connect
- Option to continue or not in case of time out
<br></br>
![image3](https://github.com/Blondie-TheManWithNoName/TFTP/assets/58909117/6e933155-5a96-46cf-9fd8-a5e9deb18569)
<br></br>
<br></br>
## **Serever Features**
<br></br>
- Set server **IP** address
- Set port
<br></br>
![image1](https://github.com/Blondie-TheManWithNoName/TFTP/assets/58909117/31d2ca2f-ed28-4bae-a426-392b082ef4c5)
<br></br>
<br></br>
- Change error message texts
- Change directory
<br></br>
![image2](https://github.com/Blondie-TheManWithNoName/TFTP/assets/58909117/87e5b1a1-c683-466f-af53-d04ce057e181)
<br></br>
<br></br>
## **Quick Demonstration**

https://github.com/Blondie-TheManWithNoName/TFTP/assets/58909117/01836cc8-60f8-40fb-ad8e-16b40c5221f3






