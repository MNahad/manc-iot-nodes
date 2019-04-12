import ina219
import usocket as socket
import ujson as json
import utime as time

start = time.ticks_ms()
sensor = ina219.INA219(scl_pin=26, sda_pin=27)
energy = 0


def res():
    data = {
        "currentInA": current,
        "voltageInV": voltage,
        "powerInW": power,
        "energyTotalInJ": energy,
    }
    return json.dumps(data)


addr = socket.getaddrinfo('192.168.4.1', 80)[0][-1]
sock = socket.socket()
sock.setblocking(0)
sock.bind(addr)
sock.listen(1)

while True:
    current = sensor.current / 1000
    voltage = sensor.bus_voltage + sensor.shunt_voltage
    end = time.ticks_ms()
    power = voltage * current
    energy += power * (time.ticks_diff(end,start)) / 1000
    start = end
    try:
        cl, addr = sock.accept()
        req = cl.makefile('rwb', 0)
        while True:
            line = req.readline()
            if not line or line == b'\r\n':
                break
        cl.send(res())
        cl.close()
    except:
        print("Comms error with client")
    time.sleep_ms(500)
