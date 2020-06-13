
                                 Light fuzzer
           ________________________________________________________
          |                   |                                    |
          |  -u*  --url       |  Target URL (required)             |
          |  -w*  --wordlist  |  Path to wordlist (required)       |
          |                   |                                    |
          |  -t   --threads   |  Number of threads (def. 40)       |
          |  -s   --delay     |  Delay between requests (ex. 0.1)  |
          |                   |                                    |
          |  -p   --payload   |  Payload string (goes after QQQ)   |
          |  -    --headers   |  Set request header (JSON format)  |
          |  -d   --data      |  Set request data                  |
          |  -m   --method    |  Set request method (def. GET)     |
          |                   |                                    |
          | --mc --match-code |  Match status code                 |
          | --ic --ignore-code|  Ignore status code                |
          |                   |                                    |
          | --ml --match-len  |  Match response length or range    |
          |                   |           ex. --ml 10000,11000     |
          | --il --ignore-len |  Ignore response length or range   |
          |                   |           ex. --il 0,1000          |
          |                   |                                    |
          |  -h   --help      |  Show this help message            |
          |___________________|____________________________________|


<h3>Installation</h3>
<code>python3 -m pip install -r requirements.txt</code><br>
<code>sudo chmod +x qzz.py</code><br>
<code>sudo ln -s /path/to/qzz/qzz.py /usr/local/bin/qzz</code><br>
<br>
<h3>Usage</h3>
    <code>qzz -u https://example.com/QQQ -w dirs.txt</code><br>
    <code>qzz -u https://QQQ.example.com -w subdomains.txt</code><br>
    <code>qzz -u https://example.com/?id=12QQQ -w wordlist.txt -p 'javascript:alert()'</code><br>
    <code>qzz -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminQQQ'</code><br>
<h5>Search files and directories</h5>
<a href="https://asciinema.org/a/337647" target="_blank"><img src="https://asciinema.org/a/337647.svg" /></a>
