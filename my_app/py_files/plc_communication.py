# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.client import ModbusTcpClient as ModbusClient

# Configure Modbus client
# client = ModbusClient(host='192.168.0.10', port=502)  # Replace with your PLC IP and port

def setup(ip_address):
    global client, connection
    client = ModbusClient(host=ip_address, port=502)  # Replace with your PLC IP and port
    connection = client.connect()
    write(0)
    print("Connected to PLC")

def write(value, address=0):
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

def close():
    client.close()
    print("Disconnected to PLC")
