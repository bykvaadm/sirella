# build
docker build -t dns-lab .

# run
docker run --name dns-lab --rm -p 5300:53/udp -p 5300:53/tcp -p 43:43 dns-lab

# test

whois -h 127.0.0.1 internal.local && \
dig @127.0.0.1 -p 5300 axfr corp.local && \
docker run --rm -it --network=host -v ./wordlist.txt:/wordlist.txt ghcr.io/oj/gobuster:latest dns -do internal.local -w /wordlist.txt --resolver 127.0.0.1:5300
