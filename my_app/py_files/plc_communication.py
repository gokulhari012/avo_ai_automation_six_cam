# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configure Modbus client
# client = ModbusClient(host='192.168.0.10', port=502)  # Replace with your PLC IP and port
ip_address = ""

def connect():
    global client, connection
    client = ModbusClient(host=ip_address, port=502)  # Replace with your PLC IP and port
    connection = client.connect()
   
def setup(ip_address_var):
    global ip_address
    ip_address = ip_address_var
    connect()
    write(1)
    time.sleep(0.5)
    write(0)
    print("Connected to PLC")
    close()

def write(value, address=0):
    connect()
    if connection:
        # Write signal (0 or 1) to Coil (Discrete Output) at address 0
        # Replace with your actual address
        client.write_coil(address, value)  # 'unit' is the slave ID

        # Read coil status
        response = client.read_coils(address)

        if response.isError():
            print("Error reading coil")
        else:
            print(f"PLC Coil Status: {response.bits[0]}")  
            # print(f"PLC Coil response: {response}")  

        print(f"Signal {value} sent to address {address}")
    else:
        print("Failed to connect to PLC")
    close()
  
def close():
    global client
    client.close()
    print("Disconnected to PLC")
