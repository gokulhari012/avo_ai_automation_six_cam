from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# Configure Modbus client
client = ModbusClient(host='192.168.0.10', port=502)  # Replace with your PLC IP and port
connection = client.connect()

if connection:
    print("Connected to PLC")

    # Write signal (0 or 1) to Coil (Discrete Output) at address 0
    address = 0  # Replace with your actual address
    value = 1    # Set to 0 or 1
    client.write_coil(address, value, unit=1)  # 'unit' is the slave ID

    print(f"Signal {value} sent to address {address}")
    client.close()
else:
    print("Failed to connect to PLC")
