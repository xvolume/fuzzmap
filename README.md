
                             Light fuzzer
       ________________________________________________________
      |                 |                                      |
      |  -u* --url      |  Target URL (required)               |
      |  -w  --wordlist |  Wordlist (def. quotlist.txt)        |
      |                 |                                      |
      |  -t  --threads  |  Number of threads (def. 40)         |
      |  -s  --delay    |  Delay between requests (ex. 0.1)    |
      |                 |                                      |
      |  -p  --payload  |  Payload string (goes after QQQ)     |
      |  -H  --headers  |  Set request header (JSON format)    |
      |  -d  --data     |  Set request data                    |
      |  -m  --method   |  Set request method (def. GET)       |
      |  --match-code   |  Match status code (def. Disabled)   |
      |                 |                                      |
      |  -h  --help     |  Show this help message              |
      |_________________|______________________________________|
    
ex.
     qzz -u https://example.com/?id=QQQ
     qzz -u https://example.com/?id=12QQQ -w wordlist.txt -p 'javascript:alert()'
     qzz -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminQQQ'
