# Simple Recon Local lab

## Prerequisites: Docker and some tools

* [docker installation guide](https://docs.docker.com/engine/install)
* dig
* whois
* nmap
* curl
* [git-dumper](https://github.com/arthaud/git-dumper)

## Start | Stop

**start:**

docker run --name sirella --rm -p 5300:53/udp -p 5300:53/tcp -p 43:43 -p 8080:80 -d bykva/sirella:latest

**stop:**

docker kill sirella

## Задачи

### Задание 1 — Проверка доступности DNS

```bash
sudo nmap -sU -p 5300 127.0.0.1
```

пример вывода:

```text
Host is up.

PORT STATE SERVICE
5300/udp open|filtered hacl-hb

Nmap done: 1 IP address (1 host up) scanned in 2.12 seconds
```

Ответ: порт 5300 открыт и доступен для взаимодействия

### Задание 2 — Определение NS и MX

1) определить NS

```bash
dig @127.0.0.1 -p 5300 corp.local NS
```

пример вывода:

```text
;; QUESTION SECTION:
;corp.local. IN NS

;; ANSWER SECTION:
corp.local. 86400 IN NS ns1.corp.local.

;; ADDITIONAL SECTION:
ns1.corp.local. 86400 IN A 192.168.100.10

;; Query time: 4 msec
;; SERVER: 127.0.0.1#5300(127.0.0.1)
;; WHEN: Sun Feb 15 19:28:28 MSK 2026
;; MSG SIZE rcvd: 73
```

Ответ: NS сервер имеет DNS ns1.corp.local и его адрес 192.168.100.10

2) определить MX

```bash
dig @127.0.0.1 -p 5300 corp.local MX
```

Ответ: mail.corp.local. 86400 IN A 192.168.100.30

### Задание 3 — Поиск поддоменов (ручной)

```bash
for dns in www mail dev vpn jira git; do dig @127.0.0.1 -p 5300 ${dns}.corp.local; done
for dns in www mail dev vpn jira git; do dig +noall +answer @127.0.0.1 -p 5300 ${dns}.corp.local; done
```

Ответ:

```text
www.corp.local. 86400 IN A 192.168.100.20
mail.corp.local. 86400 IN A 192.168.100.30
dev.corp.local. 86400 IN A 192.168.100.40
vpn.corp.local. 86400 IN A 192.168.100.50
```

### Задание 4 — Получение TXT-записей

1) Запрос TXT

```bash
dig @127.0.0.1 -p 5300 corp.local TXT
```

Ответ: corp.local. 86400 IN TXT     "v=spf1 mx -all"

2) Дополнительно

```bash
dig @127.0.0.1 -p 5300 dev.corp.local TXT
dig @127.0.0.1 -p 5300 vpn.corp.local TXT

```

Ответ:
```text
dev.corp.local. 86400 IN TXT     "Jira running on dev.corp.local:8080"
vpn.corp.local. 86400 IN TXT     "VPN-PSK: Winter2024!"

```

### Задание 5 — Проверка возможности zone transfer

```bash
dig @127.0.0.1 -p 5300 axfr corp.local
```

Ответ:
finance-db.corp.local. 86400 IN A 192.168.100.77

### Задание 6 - автоматизированное сканирование доменов

```bash
echo -e "portal\nhr\nfiles\ngit\nstaging\nwordlist.txt" > wordlist.txt
docker run --rm -it --network=host -v ./wordlist.txt:/wordlist.txt ghcr.io/oj/gobuster:latest dns -do internal.local -w
/wordlist.txt --resolver 127.0.0.1:5300
```

Ответ:

```text
git.internal.local 192.168.200.50
files.internal.local 192.168.200.40
portal.internal.local 192.168.200.20
staging.internal.local 192.168.200.60
hr.internal.local 192.168.200.30
```

### Задание 7 - обратный запрос зоны

```bash
dig @127.0.0.1 -p 5300 -x 192.168.200.121 +short
dig @127.0.0.1 -p 5300 -x 192.168.200.122 +short
dig @127.0.0.1 -p 5300 -x 192.168.200.123 +short
```

Ответ: SSsssSSSsssuperSECRET.internal.local.200.168.192.in-addr.arpa.

### Задание 8 - получение информации о домене из whois

!важно! для macos встроенный whois работать не будет - ставьте из brew нормальную свежую версию - brew install whois

```bash
whois -h 127.0.0.1 corp.local
```

Ответ:

```text
% This is a private whois server for internal use only.
% Authorized access only.
% Internal notes:
% - Default admin password for network devices is 'C0rp@dmin'
% - Backup DNS server IP: 192.168.1.12
% - VPN server: vpn.corp.local (10.10.0.5)
% - Wi-Fi SSID: CorpLocal_Employee, password: secure#W1Fi
% - FTP server (internal): ftp.corp.local (192.168.1.20) - anonymous login allowed
% - Important file: \\fileserver\share\passwords.xlsx
% - Database server: db.corp.local (10.10.0.10), test credentials: test/test
```

### Задание 9 - брутфорс найденного сайта и выкачивание git

1) open 127.0.0.1:8080 - find data in page source
2) find /robots.txt
3) check /dev_no_dict_IDDQD/ which you learned from robots.txt
4) scan website with wordlist

  ```bash
  echo -e "portal\nhr\nfiles\n.git\nstaging\nbackup" > wordlist.txt
  docker run --rm -it --network=host -v ./wordlist.txt:/wordlist.txt ghcr.io/oj/gobuster:latest \
    dir -u http://127.0.0.1:8080 -w /wordlist.txt
  ```

```text
Starting gobuster in directory enumeration mode
===============================================================
.git                 (Status: 301) [Size: 0] [--> /.git/]
backup               (Status: 301) [Size: 0] [--> /backup/]
Progress: 6 / 6 (100.00%)
```

5) check /backup/ which you learned from gobuster
6) use some kind of [git-dumper](https://github.com/arthaud/git-dumper) to dump http://127.0.0.1:8080/.git

