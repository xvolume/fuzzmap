
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
        |                 |                                      |
        |  --match-code   |  Match status code                   |
        |  --ignore-code  |  Ignore status code                  |
        |                 |                                      |
        |  -h  --help     |  Show this help message              |
        |_________________|______________________________________|


<h3>Intallation</h3>
<code>$  git clone https://github.com/xvolume/qzz.git</code><br>
<code>/qzz$  python3 -m pip install -r requirements.txt</code><br>
<code>/qzz$  sudo chmod +x qzz.py</code><br>
<code>/qzz$  sudo ln -s /path/to/qzz/qzz.py /usr/local/bin/qzz</code><br>
<br>
<h3>Examples</h3>
    <code>qzz -u https://example.com/QQQ</code><br>
    <code>qzz -u https://QQQ.example.com -w subdomains.txt</code><br>
    <code>qzz -u https://example.com/?id=12QQQ -w wordlist.txt -p 'javascript:alert()'</code><br>
    <code>qzz -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminQQQ'</code><br>
<h5>Search files and directories</h5>
<a href="https://asciinema.org/a/337647" target="_blank"><img src="https://asciinema.org/a/337647.svg" /></a>
