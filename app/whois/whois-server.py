#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WHOIS-сервер-имитация для лабораторной работы по пентесту.
Слушает порт 43 (по умолчанию) и отдаёт информацию о выдуманном домене corp.local.
Запуск: sudo python3 whois.py [port]
"""

import socket
import sys
import threading
import logging
import signal

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('whois_server')

# Информация, которую будет отдавать сервер для домена corp.local
# Информация, которую будет отдавать сервер для домена corp.local
WHOIS_RESPONSE = """Domain Name: corp.local
Registry Domain ID: 1234567890_DOM
Registrar WHOIS Server: whois.corp.local
Registrar URL: http://www.corp.local
Updated Date: 2026-02-15T10:00:00Z
Creation Date: 2020-01-01T00:00:00Z
Registry Expiry Date: 2027-01-01T00:00:00Z
Registrar: Corp Registrar LLC
Registrar IANA ID: 999
Registrar Abuse Contact Email: abuse@corp.local
Registrar Abuse Contact Phone: +1-555-123-4567
Domain Status: clientTransferProhibited
Name Server: ns1.corp.local (192.168.100.10)
Name Server: ns2.corp.local (192.168.100.11)
DNSSEC: unsigned

Registrant:
  Name: Ivan Petrov
  Organization: Corporation Local
  Street: 1234 Elm Street
  City: Springfield
  State: IL
  Postal Code: 62701
  Country: US
  Phone: +1-555-987-6543
  Email: i.petrov@corp.local

Administrative Contact:
  Name: Maria Sidorova
  Organization: Corporation Local
  Email: m.sidorova@corp.local
  Phone: +1-555-987-6544

Technical Contact:
  Name: Alex Smirnov
  Organization: Corporation Local IT Dept
  Email: a.smirnov@corp.local
  Phone: +1-555-987-6545

Billing Contact:
  Name: John Smith
  Organization: Corporation Local Finance
  Email: j.smith@corp.local
  Phone: +1-555-987-6546

inetnum: 192.168.100.0/24
netname: CORP-DMZ
descr: DMZ network (web, mail, VPN, DNS)
country: US
admin-c: ASM
tech-c: IVP
status: ASSIGNED PA
mnt-by: CORP-MNT
created: 2020-01-01
last-modified: 2026-02-15
source: CORP

inetnum: 192.168.200.0/24
netname: CORP-INTERNAL
descr: Internal corporate network (development, files, HR, staging)
country: US
admin-c: IVP
tech-c: ASM
status: ASSIGNED PA
mnt-by: CORP-MNT
created: 2020-06-01
last-modified: 2026-02-15
source: CORP

% ---- Internal notes (for IT use only) ----
%   - Backup DNS server IP: 192.168.100.11 (ns2)
%   - Wi-Fi SSID: CorpLocal_Employee, password: secure#W1Fi
%   - FTP server (internal): ftp.internal.local (192.168.200.70) - anonymous login allowed
%   - Important file: \\files.internal.local\share\passwords.xlsx
%   - Database server: db.internal.local (192.168.200.80), test credentials: test/test
%   - Jira: http://dev.corp.local:8080 (dev credentials: dev/DevPass123)
%   - Default admin credentials for network devices: admin/Admin123 (CHANGE IMMEDIATELY!)

% This is a private whois server for internal use only.
% Authorized access only.
"""

# Сообщение для несуществующих доменов
NOT_FOUND_TEMPLATE = "No entries found for domain '{}'.\r\n"


def handle_client(conn, addr):
    """Обрабатывает одно подключение клиента."""
    logger.info(f"Подключение от {addr}")
    try:
        # Получаем запрос (до символа новой строки)
        data = b''
        while not data.endswith(b'\n') and not data.endswith(b'\r\n'):
            chunk = conn.recv(1024)
            if not chunk:
                break
            data += chunk

        if not data:
            logger.info(f"Пустой запрос от {addr}, закрываем соединение")
            conn.close()
            return

        # Декодируем и очищаем запрос
        query = data.decode('ascii', errors='ignore').strip().lower()
        logger.info(f"Запрос от {addr}: {query}")

        # Формируем ответ
        if 'corp.local' in query:
            response = WHOIS_RESPONSE
        else:
            response = NOT_FOUND_TEMPLATE.format(query)

        # Отправляем ответ (WHOIS-серверы обычно закрывают соединение после ответа)
        conn.sendall(response.encode('ascii'))
    except Exception as e:
        logger.error(f"Ошибка при обработке {addr}: {e}")
    finally:
        conn.close()
        logger.info(f"Соединение с {addr} закрыто")


def run_server(port):
    """Запускает TCP-сервер на указанном порту."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', port))
    except PermissionError:
        logger.error(f"Нет прав для использования порта {port}. Попробуйте порт >1024 или запустите с sudo.")
        sys.exit(1)
    except OSError as e:
        logger.error(f"Ошибка привязки к порту {port}: {e}")
        sys.exit(1)

    server_socket.listen(5)
    logger.info(f"WHOIS-сервер запущен на порту {port}. Ожидание подключений...")

    # Обработка сигнала для корректного завершения
    def signal_handler(sig, frame):
        logger.info("Получен сигнал завершения, останавливаем сервер...")
        server_socket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        try:
            conn, addr = server_socket.accept()
            # Запускаем обработку в отдельном потоке
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
        except KeyboardInterrupt:
            logger.info("Остановка по Ctrl+C")
            break
        except Exception as e:
            logger.error(f"Ошибка при принятии соединения: {e}")

    server_socket.close()
    logger.info("Сервер остановлен")


if __name__ == '__main__':
    port = 43  # стандартный порт WHOIS
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Использование: python3 whois.py [порт]")
            sys.exit(1)

    run_server(port)
