from asyncua.sync import Client

OPC_URL = "opc.tcp://localhost:49320"

with Client(OPC_URL) as client:

    node = client.get_node(
        "ns=2;s=LP2.SYSTEM.ALARM.RELOAD_ALARM"
    )

    current = node.read_value()

    print("CURRENT =", current)

    node.write_value(int(current) + 1)

    print("WRITE OK")