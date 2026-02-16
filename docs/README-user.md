# Simple Recon Local lab

# start 
docker run --name dns-lab --rm  -p 5300:53/udp -p 5300:53/tcp -p 43:43 -p 8080:8080 -d dns-lab

# Задание 1 — Проверка доступности DNS

sirella # nmap -sU -p 5300 127.0.0.1
Host is up.

PORT     STATE         SERVICE
5300/udp open|filtered hacl-hb

Nmap done: 1 IP address (1 host up) scanned in 2.12 seconds

Ответ: порт 5300 открыт и доступен для взаимодействия

# Задание 2 — Определение NS и MX

## определить NS

% dig @127.0.0.1 -p 5300 corp.local NS

;; QUESTION SECTION:
;corp.local.                    IN      NS

;; ANSWER SECTION:
corp.local.             86400   IN      NS      ns1.corp.local.

;; ADDITIONAL SECTION:
ns1.corp.local.         86400   IN      A       192.168.100.10

;; Query time: 4 msec
;; SERVER: 127.0.0.1#5300(127.0.0.1)
;; WHEN: Sun Feb 15 19:28:28 MSK 2026
;; MSG SIZE  rcvd: 73

Ответ: NS сервер имеет DNS ns1.corp.local и его адрес 192.168.100.10

## определить MX

dig @127.0.0.1 -p 5300 corp.local MX

Ответ: mail.corp.local.        86400   IN      A       192.168.100.30


# Задание 3 — Поиск поддоменов (ручной)

for dns in www mail dev vpn jira git; do dig @127.0.0.1 -p 5300 ${dns}.corp.local; done

Ответ:

www.corp.local.         86400   IN      A       192.168.100.20
mail.corp.local.        86400   IN      A       192.168.100.30
dev.corp.local.         86400   IN      A       192.168.100.40
vpn.corp.local.         86400   IN      A       192.168.100.50


# Задание 4 — Получение TXT-записей

## Запрос TXT
dig @127.0.0.1 -p 5300 corp.local TXT
Ответ: corp.local.             86400   IN      TXT     "v=spf1 mx -all"

# Дополнительно
dig @127.0.0.1 -p 5300 dev.corp.local TXT
dig @127.0.0.1 -p 5300 vpn.corp.local TXT

Ответ:
dev.corp.local.         86400   IN      TXT     "Jira running on dev.corp.local:8080"
vpn.corp.local.         86400   IN      TXT     "VPN-PSK: Winter2024!"


# Задание 5 — Проверка возможности zone transfer

dig @127.0.0.1 -p 5300 axfr corp.local

Ответ:
finance-db.corp.local.  86400   IN      A       192.168.100.77


# Задание 6 - автоматизированное сканирование доменов

echo -e "portal\nhr\nfiles\ngit\nstaging\nwordlist.txt" > wordlist.txt
docker run --rm -it --network=host -v ./wordlist.txt:/wordlist.txt ghcr.io/oj/gobuster:latest dns -do internal.local -w /wordlist.txt --resolver 127.0.0.1:5300

Ответ:
git.internal.local 192.168.200.50
files.internal.local 192.168.200.40
portal.internal.local 192.168.200.20
staging.internal.local 192.168.200.60
hr.internal.local 192.168.200.30

# Задание 7 - обратный запрос зоны

dig @127.0.0.1 -p 5300 -x 192.168.200.121 +short
dig @127.0.0.1 -p 5300 -x 192.168.200.122 +short
dig @127.0.0.1 -p 5300 -x 192.168.200.123 +short

Ответ: SSsssSSSsssuperSECRET.internal.local.200.168.192.in-addr.arpa.

# Задание 8 - получение информации о домене из whois
!важно! для macos встроенный whois работать не будет - ставьте из brew нормальную свежую версию - brew install whois

whois -h 127.0.0.1 corp.local

Ответ:

% This is a private whois server for internal use only.
% Authorized access only.
% Internal notes:
%   - Default admin password for network devices is 'C0rp@dmin'
%   - Backup DNS server IP: 192.168.1.12
%   - VPN server: vpn.corp.local (10.10.0.5)
%   - Wi-Fi SSID: CorpLocal_Employee, password: secure#W1Fi
%   - FTP server (internal): ftp.corp.local (192.168.1.20) - anonymous login allowed
%   - Important file: \\fileserver\share\passwords.xlsx
%   - Database server: db.corp.local (10.10.0.10), test credentials: test/test

# Задание 9 - брутфорс найденного сайта и выкачивание git

- брутим dev.corp.local:8080
- находим /.git
- выкачиваем гит
- находим пароль



{
  "log": {
    "access": "./access.log",
    "dnsLog": false,
    "error": "./error.log",
    "loglevel": "debug",
    "maskAddress": ""
  },
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {
        "type": "field",
        "inboundTag": [
          "api"
        ],
        "outboundTag": "api"
      },
      {
        "type": "field",
        "outboundTag": "blocked",
        "ip": [
          "geoip:private"
        ]
      },
      {
        "type": "field",
        "outboundTag": "blocked",
        "protocol": [
          "bittorrent"
        ]
      }
    ]
  },
  "dns": null,
  "inbounds": [
    {
      "listen": "127.0.0.1",
      "port": 62789,
      "protocol": "dokodemo-door",
      "settings": {
        "address": "127.0.0.1"
      },
      "streamSettings": null,
      "tag": "api",
      "sniffing": null
    },
    {
      "listen": "11.22.33.44",
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "email": "bykva_iphone",
            "flow": "",
            "id": "123123-123-123-123-123123"
          }
        ],
        "decryption": "none",
        "fallbacks": []
      },
      "streamSettings": {
        "network": "xhttp",
        "realitySettings": {
          "dest": "apple.com:443",
          "maxClient": "",
          "maxTimediff": 0,
          "minClient": "",
          "privateKey": "cOfIJwL_ArgF0aLHweijqwfOIHliqnwfoihIUOGqwofmej",
          "serverNames": [
            "www.apple.com",
            "apple.com"
          ],
          "shortIds": [
            "25807c",
            "bf3eb0b353c6",
            "4ff46b4a14022bbd",
            "81",
            "335c265df2",
            "8dfc",
            "f019ef29",
            "ef51e121a0b42b"
          ],
          "show": false,
          "xver": 0
        },
        "security": "reality",
        "xhttpSettings": {
          "headers": {},
          "host": "",
          "mode": "auto",
          "noSSEHeader": false,
          "path": "/",
          "scMaxBufferedPosts": 30,
          "scMaxEachPostBytes": "1000000",
          "scStreamUpServerSecs": "20-80",
          "xPaddingBytes": "100-1000"
        }
      },
      "tag": "inbound-44.33.22.11:443",
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls",
          "quic",
          "fakedns"
        ],
        "metadataOnly": false,
        "routeOnly": false
      }
    }
  ],
  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom",
      "settings": {
        "domainStrategy": "AsIs",
        "redirect": "",
        "noises": []
      }
    },
    {
      "tag": "blocked",
      "protocol": "blackhole",
      "settings": {}
    }
  ],
  "transport": null,
  "policy": {
    "levels": {
      "0": {
        "statsUserDownlink": true,
        "statsUserUplink": true
      }
    },
    "system": {
      "statsInboundDownlink": true,
      "statsInboundUplink": true,
      "statsOutboundDownlink": true,
      "statsOutboundUplink": true
    }
  },
  "api": {
    "tag": "api",
    "services": [
      "HandlerService",
      "LoggerService",
      "StatsService"
    ]
  },
  "stats": {},
  "reverse": null,
  "fakedns": null,
  "observatory": null,
  "burstObservatory": null,
  "metrics": null