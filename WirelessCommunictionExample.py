# -*- coding: utf-8 -*-
#####################################################################################################
# Author    : Alexandre Ribault                                                                     #
# M@il      : AlexandreRibault87@gmail.com                                                          #
# Date      : 11/28/2020                                                                            #
# Function  : Communicate with Robitino by contacting Robitino View                                 #
#####################################################################################################
#                                                                                                   #
#                               DISPLAY OPTIMISED FOR NOTEPAD++                                     #
#                                                                                                   #
#####################################################################################################


"""

	Copyright (c) 2024 Alexandre Ribault	

	The methods you find in this file are free: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

	It is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

	You should have received a copy of the GNU General Public License along with this file. If not, see <https://www.gnu.org/licenses/>

"""

#####################################################################################################
#                                  LIBRARIES IMPORT                                                 #
#####################################################################################################
import socket
import sys

#####################################################################################################
#                                       CONSTANTS                                                   #
#####################################################################################################
MAX_VALUE_UINT8         = 256
MAX_VALUE_ON_4_BITS     = 16
MINIMAL_CHECKSUM_CANAL0 = 36
MINIMAL_CHECKSUM_CANAL1 = 37
MAX_VALUE_UINT32        = 4294967295
MAX_VALUE_UINT8_EXP4    = MAX_VALUE_UINT8**4
MAX_VALUE_UINT8_EXP3    = MAX_VALUE_UINT8**3
MAX_VALUE_UINT8_EXP2    = MAX_VALUE_UINT8**2
CANAL0                  = 0
CANAL1                  = 1
INPUT0                  = 0
INPUT1                  = 1
INPUT2                  = 2
INPUT3                  = 3
INPUT4                  = 4
INPUT5                  = 5
INPUT6                  = 6
INPUT7                  = 7
HEX_CHAR =[ '0', '1', '2', '3', '4', '5', '6','7','8', '9', 'a', 'b', 'c', 'd', 'e','f' ]


#####################################################################################################
#                                       METHODS                                                    #
#####################################################################################################

#####################################################################################################
# Method            : getMessageToSend                                                              #
# Purpose           : Create a message wich contains the value to send to Robotino View'server      #
# Return value type : Bytes                                                                         #
#####################################################################################################
def getMessageToSend(ID_Message,input0,input1,input2,input3,input4,input5,input6,input7):
    # ID_Message permits to choose wich canal you want to use beetween the '0' or the '1'
    # Variables init
    
    InputTable=[input0,input1,input2,input3,input4,input5,input6,input7]    
    valuesToString="" #Variable to save the conversion result
    messageToSendToRobotinoView=''
    i=0
    # End init
    
    # Start
    if ID_Message==0:
        messageToSendToRobotinoView="0024"
        checksum= MINIMAL_CHECKSUM_CANAL0
    if  ID_Message==1:
        messageToSendToRobotinoView="0124"
        checksum= MINIMAL_CHECKSUM_CANAL1

    #8 , because we manage 8 inputs.
    while(i<8) :  # A for loop would be better here
        if (InputTable[i]<0):# If you send a negative Value, you have to use 'Two's complement' method
            InputTable[i]=(MAX_VALUE_UINT32+ InputTable[i] +1) #Using this MAX_VALUE_UINT32 ensures to have a '1' at the MSB postion, wich means a negative value for a Int32            

        # This part of code permit to "translate" Integer value in decimal base, to Hexadecimal base(as string, no more as integer)		
        Byte3=(int(InputTable[i]/(MAX_VALUE_UINT8_EXP3)))
        checksum+=Byte3
        			
        InputTable[i]=InputTable[i]%(MAX_VALUE_UINT8_EXP3)
        Byte2=(int(InputTable[i]/(MAX_VALUE_UINT8_EXP2)))
        checksum+=Byte2
        			
        InputTable[i]=InputTable[i]%(MAX_VALUE_UINT8_EXP2)#;
        Byte1=(int(InputTable[i]/(MAX_VALUE_UINT8)))
        checksum+=Byte1
    			
        InputTable[i]=InputTable[i]%MAX_VALUE_UINT8
        Byte0=(InputTable[i])
        checksum+=Byte0
            
        valuesToString+=  HEX_CHAR[int(Byte0/MAX_VALUE_ON_4_BITS)]+HEX_CHAR[int(Byte0%MAX_VALUE_ON_4_BITS)]+ HEX_CHAR[int(Byte1/MAX_VALUE_ON_4_BITS)]+HEX_CHAR[int(Byte1%MAX_VALUE_ON_4_BITS)]+ HEX_CHAR[int(Byte2/MAX_VALUE_ON_4_BITS)]+HEX_CHAR[int(Byte2%MAX_VALUE_ON_4_BITS)]+ HEX_CHAR[int(Byte3/MAX_VALUE_ON_4_BITS)]+HEX_CHAR[int(Byte3%MAX_VALUE_ON_4_BITS)]
        i=i+1 # When i= 8, all inputs are managed. 

    # The checksum is on a Byte only. Refer to Robotino View's documention
    checksum= 0xFF-(checksum%MAX_VALUE_UINT8)
    checksumToString= HEX_CHAR[(int(checksum/MAX_VALUE_ON_4_BITS))]+HEX_CHAR[(int(checksum%MAX_VALUE_ON_4_BITS))] # Convert the int value of Checksum to string
    messageToSendToRobotinoView+=checksumToString +valuesToString    
    return bytes.fromhex(messageToSendToRobotinoView)

#####################################################################################################
# Method            : readOutput                                                                    #
# Purpose           : Convert Bytes to int. Correspond of the outputX value(where x= 0 to 7)        #
# Return value type : int                                                                           #
#####################################################################################################    
def readOutput(Data,inputX):
    canal =  Data[0]
    # An input is coded on 4 Bytes. 
    startingByte=4+4*inputX  # Permits to index  the first ou the four Bytes
    Bytes = Data[startingByte:startingByte+4] #This line permits to sort only the 4 Bytes used to code inputX's value
    #print(str(Bytes))
    if int(Bytes[3])>=0x80: # If greater of equal to 0x80( or 128), it means the MSB is equal to 1 => InputX is
        intToReturn=-((MAX_VALUE_UINT8**4) -(int(Bytes[0])+(MAX_VALUE_UINT8*int(Bytes[1])) +(MAX_VALUE_UINT8**2*int(Bytes[2])+ (MAX_VALUE_UINT8**3*int(Bytes[3])))))
    else:
        intToReturn=int(Bytes[0])+(MAX_VALUE_UINT8*int(Bytes[1])) +(MAX_VALUE_UINT8**2*int(Bytes[2])+ (MAX_VALUE_UINT8**3*int(Bytes[3])))
    return "CANAL{0}".format(canal),intToReturn    

#####################################################################################################
#                                                                                                   #
#                                                   MAIN                                            #
#                                                                                                   #
#####################################################################################################

#This code is not a complet implentation of a goof communication beetween client and server.
# It permit only  to demonstrate how to exchange data between client and server

# Ther server's configuration is done in "Robotino View"'s project


# client's configuration
UDP_IP='localhost' # mean '127.0.01', it's your local IP
UDP_PORT_EMISSION   =9180
UDP_PORT_RECEPTION = 9182
mySocket_Emission   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySocket_Reception  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySocket_Reception.bind((UDP_IP, UDP_PORT_RECEPTION))

# Emission
message=getMessageToSend(CANAL0,255,0,-1759,0,-255,0,8000,0) 
mySocket_Emission.sendto(message, (UDP_IP, UDP_PORT_EMISSION))

message=getMessageToSend(CANAL1,255,0,-1759,0,-255,0,8000,0) 
mySocket_Emission.sendto(message, (UDP_IP, UDP_PORT_EMISSION))

#Reception : 
while(1):
    data, addr = mySocket_Reception.recvfrom(2048)    
    print ("conv=" +str(readOutput(data,INPUT4))) # Will read the output 0. You choose 0, 1, 2, .., 7

# Closing server communication
mySocket_Emission.close()
mySocket_Reception.close()
