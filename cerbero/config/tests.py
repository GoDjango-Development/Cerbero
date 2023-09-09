import socket
from time import sleep, time, process_time
from icmplib import ping


def prueba(ip):
    for _ in range(30):
        try:
            start_time = time()

            icmp = ping(ip, count=3, interval=2, timeout=5)
            if icmp.is_alive:
                result = "up"
            else:
                result = "down"

            end_time = time()
            processing_time = end_time - start_time
            print(f"Tiempo de procesamiento: {processing_time}")

        except Exception as e:
            print(f"Error de conexión: {str(e)}")
            result = "error"
            processing_time = 0
        print(result)
        sleep(1)

    return result


prueba("10.8.27.207")
