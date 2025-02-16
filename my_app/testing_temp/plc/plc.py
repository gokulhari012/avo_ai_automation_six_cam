# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.client import ModbusTcpClient as ModbusClient

# Configure Modbus client
# client = ModbusClient(host='192.168.0.10', port=502)  # Replace with your PLC IP and port
client = ModbusClient(host='169.254.225.8', port=502)  # Replace with your PLC IP and port
connection = client.connect()

if connection:
    print("Connected to PLC")
    for i in range (0,0):
        # Write signal (0 or 1) to Coil (Discrete Output) at address 0
        address = i  # Replace with your actual address
        value = 1        # Set to 0 or 1
        client.write_coil(address, value)  # 'unit' is the slave ID

        # Read coil status
        response = client.read_coils(address)

        # if response.isError():
        #     print("Error reading coil")
        # else:
        #     # print(f"PLC Coil Status: {response.bits[0]}")  
        #     print(f"PLC Coil response: {response}")  

        print(f"Signal {value} sent to address {address}")
    
    register_address = 4  # Not required
    value = 1
    client.write_register(register_address, value)  # 'unit' is the slave ID

    register_address = 3  # Not required
    value = 1
    client.write_register(register_address, value)  # 'unit' is the slave ID

    register_address = 0  # Example: D100 in Delta PLC
    value = 1000
    value = 0
    client.write_register(register_address, value)  # 'unit' is the slave ID

    register_address = 1  # Example: D100 in Delta PLC
    value = 0
    client.write_register(register_address, value)  # 'unit' is the slave ID

    register_address = 2  # Example: D100 in Delta PLC
    value = 1
    client.write_register(register_address, value)  # 'unit' is the slave ID
    
    
    # Read coil status
    register_address = 2
    response = client.read_holding_registers(register_address)
    print(f"Signal {response.registers[0]} sent to address {register_address}")
    
    client.close()
else:
    print("Failed to connect to PLC")
