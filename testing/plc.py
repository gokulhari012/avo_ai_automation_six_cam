# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.client import ModbusTcpClient as ModbusClient

# Configure Modbus client
# client = ModbusClient(host='192.168.0.10', port=502)  # Replace with your PLC IP and port
client = ModbusClient(host='169.254.109.8', port=502)  # Replace with your PLC IP and port
connection = client.connect()

if connection:
    print("Connected to PLC")
    for i in range (0,1):
        # Write signal (0 or 1) to Coil (Discrete Output) at address 0
        address = i  # Replace with your actual address
        value = 0    # Set to 0 or 1
        client.write_coil(address, value)  # 'unit' is the slave ID

        # Read coil status
        response = client.read_coils(address)

        # if response.isError():
        #     print("Error reading coil")
        # else:
        #     # print(f"PLC Coil Status: {response.bits[0]}")  
        #     print(f"PLC Coil response: {response}")  

        print(f"Signal {value} sent to address {address}")
    
    client.close()
else:
    print("Failed to connect to PLC")
