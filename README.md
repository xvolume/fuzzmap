
                             Light fuzzer
       ________________________________________________________
      |                 |                                      |
      |  -u* --url      |  Target URL (required)               |
      |  -w  --wordlist |  Wordlist (def. dirs_common.txt)     |
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
    
    
##Intallation<br>
'''git clone https://github.com/xvolume/qzz.git'''
In qzz dir
'''python3 -m pip install -r requirements.txt'''
'''sudo chmod +x qzz'''
'''sudo ln -s /path/to/qzz/qzz /usr/local/bin/qzz'''
<br>
##Example<br>
    '''qzz -u https://example.com/QQQ'''<br>
    qzz -u https://example.com/?id=12QQQ -w wordlist.txt -p 'javascript:alert()'<br>
    qzz -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminQQQ'<br>
