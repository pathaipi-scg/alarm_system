from pyModbusTCP.client import ModbusClient

c = ModbusClient(
    host="172.28.231.251",   # หรือ IP Modbus Server
    port=502,
    auto_open=True
)

# 412003 => Holding Register 2002
regs = c.read_holding_registers(12002, 1)

print(regs)

c.write_single_register(
    12002,
    regs[0] + 1
)

print("WRITE OK")