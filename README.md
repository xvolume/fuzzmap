<h3>Installation</h3>
<code>git clone https://github.com/xvolume/fuzzmap.git</code><br>
<code>cd fuzzmap/</code><br>
<code>chmod +x fuzzmap.py</code><br>
<code>pip install -r requirements.txt</code><br>
<code>ln -s /path/to/fuzzmap/fuzzmap.py ~/.local/bin/fuzzmap</code><br>
<br>
<h3>Usage</h3>
    <code>fuzzmap -u https://example.com/FUZZ -w dirs.txt</code><br>
    <code>fuzzmap -u https://FUZZ.example.com -w subdomains.txt</code><br>
    <code>fuzzmap -u https://example.com/?id=12FUZZ -w wordlist.txt -p 'javascript:alert()'</code><br>
    <code>fuzzmap -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminFUZZ'</code><br>
<h5>Search files and directories</h5>
<a href="https://asciinema.org/a/339470" target="_blank"><img src="https://asciinema.org/a/339470.svg" /></a>
<br>
<h3>Help</h3>

                                   FUZZmap
                             by @xvolume/@avolume

           ________________________________________________________
          |                   |                                    |
          |  -u*  --url       |  Target URL (required)             |
          |  -w*  --wordlist  |  Path to wordlist (required)       |
          |                   |                                    |
          |  -t   --threads   |  Number of threads (def. 40)       |
          |  -s   --delay     |  Delay between requests (ex. 0.1)  |
          |                   |                                    |
          |  -p   --payload   |  Payload string (goes after FUZZ)  |
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
<h3>TODO</h3>
<ul>
    <li>  Base64 support</li>
    <li>  Url list support</li>
    <li>? Payload list support</li>
    <li>  Raw request support (ex. from Burp)</li>
    <li>  Crawler</li>
    <li>  Smart fuzz (based on response size)</li>
    <li>? Bruteforce by request method</li>
</ul>
