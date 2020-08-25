# FUZZmap

```
                   __ ___________  ____________
     )         __  ___  ____/_  / / /__  /__  /__________________
    /(  )         ___  /_  __  / / /__  /__  /__     \  __ `  __ \
   (  )( )  )      _  __/   / /_/ /__  /__  /__  / / / /_/ / /_/ /
  ( \( (  )/ )___  /_/   ___\____/  /____/____/_/_/_/\__,_/ .___/
                                                         __/
```


## Installation
```
git clone https://github.com/xvolume/fuzzmap.git
cd fuzzmap/
chmod +x fuzzmap.py
pip install -r requirements.txt
ln -s /path/to/fuzzmap/fuzzmap.py ~/.local/bin/fuzzmap
```
## Usage
**Finding directories**
```
fuzzmap -u https://example.com/FUZZ -w dirs.txt --output output.json
```
**Discovering subdomains**
```
fuzzmap -u https://FUZZ.example.com -w subdomains.txt --match-code all
```
**Fuzzing params**
```
fuzzmap -u https://example.com/?q=FUZZ -w wordlist.txt --mc 200,301,302
```
```
fuzzmap -u https://example.com -w wl.txt -m POST -H '{"Cookie": "Q29va2llCg=="}' -d 'user=FUZZ'
```
**Parsing output**
```
fuzzmap --parse output.json
```
```
fuzzmap --parse output.json --match-code 200
```
## Help

```
        __________________________________________________________
       |                     |                                    |
       |   -u   --url        |  Target URL (required)         !   |
       |   -w   --wordlist   |  Path to wordlist (required)   !   |
       |                     |                                    |
       |   -t   --threads    |  Number of threads (def. 40)       |
       |   -s   --delay      |  Delay between requests (ex. 0.1)  |
       |                     |                                    |
       |   -p   --payload    |  Payload string (goes after FUZZ)  |
       |   -    --headers    |  Set request header (JSON format)  |
       |   -d   --data       |  Set request data                  |
       |   -m   --method     |  Set request method (def. GET)     |
       |                     |                                    |
       | --mc --match-code   |  Match status code. Set 'all' to   |
       |                     |  match all codes.                  |
       | --ic --ignore-code  |  Ignore status code                |
       |                     |                                    |
       | --ml --match-len    |  Match response length or range    |
       |                     |                                    |
       | --il --ignore-len   |  Ignore response length or range   |
       |                     |                                    |
       | --mw --match-words  |  Match resp. words count or range  |
       |                     |                                    |
       | --iw --ignore-words |  Ignore resp. words count or range |
       |                     |                                    |
       | --mli --match-lines |  Match resp. lines count or range  |
       |                     |                                    |
       | --ili --ignore-lines|  Ignore resp. lines count or range |
       |                     |      ex.                           |
       |                     |  --mc all --iw 110,124 --il 0-100  |
       |                     |                                    |
       |      --parse        |  Parse output file. You can use it |
       |                     |  with --match-code.                |
       |                     |      ex. --parse result.json       |
       |                     |                                    |
       |   -o   --output     |  Write output to file (JSON)       |
       |   -h   --help       |  Show this help message            |
       |_____________________|____________________________________|

```

## TODO


<ul>
    <li>  Add proxy</li>
    <li>  Base64 support</li>
    <li>  Url list support</li>
    <li>  Raw request support (ex. from Burp)</li>
    <li>  Smart fuzz (based on response size)</li>
    <li>? Bruteforce by request method if 401</li>
</ul>
