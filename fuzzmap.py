#!/usr/bin/python3
import sys, getopt
import workerpool
import urllib3, json
import datetime, time
import os.path


WORDLIST = None
THREADS = 50
SLEEP = None
METHOD = 'GET'
HEADER = None
DATA = None
#REQUEST = None
PAYLOAD = ''
URL = None
FUZZ = None
OUTFILE = None
OUTDATA = ''
SETTINGS = None
MATCH_CODE = None #[200,204,301,302,307]
IGNORE_CODE = None
MATCH_LEN = None
IGNORE_LEN = None
MATCH_WORDS = None
IGNORE_WORDS = None
MATCH_LINES = None
IGNORE_LINES = None
COUNTER = 0
ERRORS_COUNTER = 0

allowed_methods = [
	'OPTIONS',
	'GET',
	'HEAD',
	'POST',
	'PUT',
	'DELETE',
	'TRACE',
	'CONNECT',
	'PROPFIND',
	'PROPPATCH',
	'MKCOL',
	'COPY',
	'MOVE',
	'LOCK',
	'UNLOCK',
	'VERSION-CONTROL',
	'REPORT',
	'CHECKOUT',
	'CHECKIN',
	'UNCHECKOUT',
	'MKWORKSPACE',
	'UPDATE',
	'LABEL',
	'MERGE',
	'BASELINE-CONTROL',
	'MKACTIVITY',
	'ORDERPATCH',
	'ACL',
	'PATCH',
	'SEARCH']


def main():
	global WORDLIST
	global THREADS
	global SLEEP
	global METHOD
	global HEADER
	global DATA
#	global REQUEST
	global PAYLOAD
	global URL
	global MATCH_CODE
	global IGNORE_CODE
	global MATCH_LEN
	global IGNORE_LEN
	global MATCH_WORDS
	global IGNORE_WORDS
	global MATCH_LINES
	global IGNORE_LINES
	global FUZZ
	global OUTFILE

	try:
		opts, args = getopt.getopt(
			sys.argv[1:],
			"hu:w:t:s:p:H:d:m:o:",[
				"help",
				"url=",
				"wordlist=",
				"threads=",
				"delay=",
				"payload=",
				"headers=",
				"data=",
				"method=",
				"output=",
				"mc=",
				"match-code=",
				"ic=",
				"ignore-code=",
				"ml=",
				"match-len=",
				"il=",
				"ignore-len=",
				"mw=",
				"match-words=",
				"iw=",
				"ignore-words=",
				"mli=",
				"match-lines=",
				"ili=",
				"ignore-lines="])

		for opt, arg in opts:
			arg = arg.strip()
			if opt in ("-h", "--help"):
				help()
			elif opt in ("-u", "--url"):
				URL = arg
			elif opt in ("-w", "--wordlist"):
				if os.path.isfile(arg):
					WORDLIST = arg
				else:
					help(f"Error: wordlist {arg} not found\n")
			elif opt in ("-t", "--threads"):
				THREADS = int(arg)
			elif opt in ("-s", "--delay"):
				SLEEP = float(arg)
			elif opt in ("-p", "--payload"):
				PAYLOAD = arg
			elif opt in ("-H", "--headers"):
				HEADER = arg
			elif opt in ("-d", "--data"):
				DATA = arg
			elif opt in ("-m", "--method"):
				if arg.upper() in allowed_methods:
					METHOD = arg.upper()
				else:
					help(f"Error: method {arg.strip()} not allowed\n")
			elif opt in ("--mc", "--match-code"):
				if str(arg.strip()) != 'all':
					MATCH_CODE = [int(i.strip()) for i in arg.split(',')]
				else:
					MATCH_CODE = arg.strip()
			elif opt in ("--ic", "--ignore-code"):
				IGNORE_CODE = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("--ml", "--match-len"):
				if ',' in arg:
					MATCH_LEN = [int(i.strip()) for i in arg.split(',')]
				else:
					MATCH_LEN = arg.strip()
			elif opt in ("--il", "--ignore-len"):
				if ',' in arg:
					IGNORE_LEN = [int(i.strip()) for i in arg.split(',')]
				else:
					IGNORE_LEN = arg.strip()
			elif opt in ("--mw", "--match-words"):
				if ',' in arg:
					MATCH_WORDS = [int(i.strip()) for i in arg.split(',')]
				else:
					MATCH_WORDS = arg.strip()
			elif opt in ("--iw", "--ignore-words"):
				if ',' in arg:
					IGNORE_WORDS = [int(i.strip()) for i in arg.split(',')]
				else:
					IGNORE_WORDS = arg.strip()
			elif opt in ("--mli", "--match-lines"):
				if ',' in arg:
					MATCH_LINES = [int(i.strip()) for i in arg.split(',')]
				else:
					MATCH_LINES = arg.strip()
			elif opt in ("--ili", "--ignore-lines"):
				if ',' in arg:
					IGNORE_LINES = [int(i.strip()) for i in arg.split(',')]
				else:
					IGNORE_LINES = arg.strip()
			elif opt in ("-o", "--output"):
				OUTFILE = arg.strip()
#			elif opt == "-r":
#				if os.path.isfile(arg):
#					f = open(arg)
#					REQUEST = f.read()
#					f.close()
			else:
				help(f"Error: [{opt}] unhandled option\n")

		if URL is None:
			help("Error: method [-u --url] is required\n")
		if WORDLIST is None:
			help("Error: method [-w --wordlist] is required\n")

# Impossible to discover subdomains with this validation
#		try:
#			urllib3.PoolManager().request(METHOD, URL.replace('FUZZ', ''))
#		except Exception as e:
#			help(f"Error: {URL} connection failed\n")

		if 'FUZZ' in ( str(URL) + str(HEADER) + str(DATA) ):
			default_MATCH_CODES = None

			if MATCH_CODE is None and IGNORE_CODE is None:
				default_MATCH_CODES = [200,204,301,302,307]

			banner(URL, METHOD, WORDLIST, THREADS, SLEEP, PAYLOAD, HEADER,
				DATA, default_MATCH_CODES, IGNORE_CODE, MATCH_LEN, IGNORE_LEN,
				MATCH_WORDS, IGNORE_WORDS, MATCH_LINES, IGNORE_LINES, OUTFILE)

			FUZZ = [i.strip('\n') for i in open(WORDLIST).readlines()]

			url, header, data = prepare_requests(URL, FUZZ, HEADER, DATA)

			pool = workerpool.WorkerPool(size=THREADS)
			pool.map(send_request, url, header, data)
			pool.shutdown()
			pool.wait()

			save_output(OUTFILE, SETTINGS, OUTDATA)

			print('\n')
		else:
			help(f"Error: 'FUZZ' not found.\n"+
				"\tex: -u http://example.com/FUZZ (Accepted in url, header and data fields)")

	except Exception as ex:
		help('Error: '+str(ex)+'\n')


def output(url, redirect, status, length, words, lines, time):
	global OUTDATA

	url = json.dumps(url)
	redirect = json.dumps(redirect)
	status = json.dumps(status)
	length = json.dumps(length)
	words = json.dumps(words)
	lines = json.dumps(lines)
	time = json.dumps(time)

	if len(OUTDATA) == 0:
		OUTDATA = '{'
	else:
		OUTDATA += ',{'
	OUTDATA += f'"url":{url},"redirect":{redirect},"status":{status},"length":{length},"words":{words},"lines":{lines},"time":{time}'
	OUTDATA += '}'


def save_output(file, settings, results):
	date = datetime.datetime.now().strftime("%d/%m/%y %H:%M")

	if file and settings and results:
		data = f'"settings":{settings},"results":[{results}],"date":"{date}"'
		data_len = str(len(data)+2)
		try:
			with open(file, 'w') as f:
				f.write('{'+data+'}')
			print(f'\nOutput saved to {file}\nTotal: {data_len} bytes')
		except Exception as e:
			help(str(e))


def printer(url, r=None):
	progress = str(COUNTER)+'/'+str(len(FUZZ))
	fuzz = url.split("//")[1]
	t = time.strftime('%H:%M:%S', time.gmtime(time.time()-start_time))
	len_data = len(r.data) if r else None
	words_data = len(str(r.data).split(' ')) if r else None
	lines_data = len(str(r.data).split('\n')) if r else None
	status = r.status if r else None
	redirect = r.get_redirect_location() if r and r.get_redirect_location() else None


	if MATCH_CODE and str(MATCH_CODE) == 'all' and IGNORE_CODE is None or\
		MATCH_CODE and str(MATCH_CODE) == 'all' and IGNORE_CODE and status not in IGNORE_CODE:
		if len_check(MATCH_LEN, IGNORE_LEN, len_data) and\
			len_check(MATCH_WORDS, IGNORE_WORDS, words_data) and\
			len_check(MATCH_LINES, IGNORE_LINES, lines_data):
			if OUTFILE and status and len_data and words_data and lines_data:
				output(url, redirect, status, len_data, words_data, lines_data, t)
			print(f'\r {fuzz:48}|{str(status):^5}'+
				f'|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}| {t:20}', end='\n')

	elif MATCH_CODE and str(MATCH_CODE) != 'all' and status in MATCH_CODE and IGNORE_CODE is None or\
		IGNORE_CODE and status not in IGNORE_CODE and MATCH_CODE is None or\
		MATCH_CODE and IGNORE_CODE and str(MATCH_CODE) != 'all' and status in MATCH_CODE and status not in IGNORE_CODE:
		if len_check(MATCH_LEN, IGNORE_LEN, len_data) and\
			len_check(MATCH_WORDS, IGNORE_WORDS, words_data) and\
			len_check(MATCH_LINES, IGNORE_LINES, lines_data):
			if OUTFILE and status and len_data and words_data and lines_data:
				output(url, redirect, status, len_data, words_data, lines_data, t)
			print(f'\r {fuzz:48}|{str(status):^5}'+
				f'|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}| {t:20}', end='\n')

	elif MATCH_CODE is None and IGNORE_CODE is None:
		if status in [200,204,301,302,307]:
			if len_check(MATCH_LEN, IGNORE_LEN, len_data) and\
				len_check(MATCH_WORDS, IGNORE_WORDS, words_data) and\
				len_check(MATCH_LINES, IGNORE_LINES, lines_data):
				if OUTFILE and status and len_data and words_data and lines_data:
					output(url, redirect, status, len_data, words_data, lines_data, t)
				print(f'\r {fuzz:48}|{str(status):^5}'+
					f'|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}| {t:20}', end='\n')

	print(f'\r {fuzz[:33]:34}{progress:^14}'+
		f'|{str(status):^5}|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}'+
		f'|{t:^10}'+
		f' {"Err: "+str(ERRORS_COUNTER)}', end='')


def len_check(match, ignore, len):
	if match and ignore is None:
		if type(match) is list:
			return int(len) in range(match[0], match[1])
		else:
			return int(len) == int(match)

	elif ignore and match is None:
		if type(ignore) is list:
			return int(len) not in range(ignore[0], ignore[1])
		else:
			return int(len) != int(ignore)

	elif match and ignore:
		if type(match) is list and type(ignore) is list:
			return int(len) in range(match[0], match[1]) and\
				int(len) not in range(ignore[0], ignore[1])
		elif type(match) is list:
			return int(len) in range(match[0], match[1]) and\
				int(len) != int(ignore)
		elif type(ignore) is list:
			return int(len) not in range(ignore[0], ignore[1]) and\
				int(len) == int(match)
		else:
			return int(len) == int(match) and int(len) != int(ignore)

	elif match is None and ignore is None:
		return True


http = urllib3.PoolManager(maxsize = int(THREADS*0.6))
start_time = time.time()

def send_request(url, header, data):
	global COUNTER
	global ERRORS_COUNTER
	COUNTER += 1

	if SLEEP:
		time.sleep(SLEEP)

	try:
		r = http.request(
			METHOD,
			url,
			headers = header,
			body = data,
			timeout = 10,
			retries = False,
			redirect = False)
		printer(url, r)
	except:
		printer(url)
		ERRORS_COUNTER += 1


def prepare_requests(url, FUZZ, header=None, data=None):
	u = []
	h = []
	d = []

	for q in FUZZ:
		if 'FUZZ' in url:
			u.append( url.replace('FUZZ', q+PAYLOAD) )
		else:
			u.append( url )

		if header:
			if 'FUZZ' in header:
				head = header.replace('FUZZ', q+PAYLOAD)
			try:
				h.append( json.loads(head) )
			except:
				h.append( None )
		else:
			h.append( header )

		if data:
			d.append( data.replace('FUZZ', q+PAYLOAD))
		else:
			d.append( data )


	return u, h, d


def logo():
	print("""
                 __ ___________  ____________
   )         __  ___  ____/_  / / /__  /__  /__________________
  /(  )         ___  /_  __  / / /__  /__  /__     \  __ `  __ \\
 (  )( )  )      _  __/   / /_/ /__  /__  /__  / / / /_/ / /_/ /
( \( (  )/ )___  /_/   ___\____/  /____/____/_/_/_/\__,_/ .___/
                                                       __/

                            FUZZmap
                      by @xvolume/@avolume
""")


def banner(u, m, w, t, s, p, H, d, mc, ic, ml, il, mw, iw, mli, ili, o):
	global SETTINGS

	SETTINGS = '{'
	SETTINGS += f'"target":{json.dumps(u)},'
	SETTINGS += f'"method":{json.dumps(m)},'
	SETTINGS += f'"wordlist":{json.dumps(w)},'
	SETTINGS += f'"threads":{json.dumps(t)},'
	SETTINGS += f'"delay":{json.dumps(str(s))},' if s else ''
	SETTINGS += f'"payload":{json.dumps(p)},' if p else ''
	SETTINGS += f'"headers":{json.dumps(H)},' if H else ''
	SETTINGS += f'"data":{json.dumps(d)},' if d else ''
	SETTINGS += f'"match_code":{json.dumps(mc)},' if mc else ''
	SETTINGS += f'"ignore_code":{json.dumps(ic)},' if ic else ''
	SETTINGS += f'"match_len":{json.dumps(str(ml))},' if ml else ''
	SETTINGS += f'"ignore_len":{json.dumps(str(il))},' if il else ''
	SETTINGS += f'"match_words":{json.dumps(str(mw))},' if mw else ''
	SETTINGS += f'"ignore_words":{json.dumps(str(iw))},' if iw else ''
	SETTINGS += f'"match_lines":{json.dumps(str(mli))},' if mli else ''
	SETTINGS += f'"ignore_lines":{json.dumps(str(ili))},' if ili else ''
	SETTINGS += f'"output_file":{json.dumps(str(o))}' if o else ''
	SETTINGS += '}'

	logo()
	print(f"""
                           Loaded up
     ______________________________________________________
    |                                                      |
    |  URL         ::  {u:36}|
    |  METHOD      ::  {m:36}|
    |  WORDLIST    ::  {w:36}|
    |  THREADS     ::  {str(t):36}|""")
	print(f"    |  DELAY       ::  {str(s):36}|") if s else None
	print(f"    |  PAYLOAD     ::  {p:36}|")if p else None
	print(f"    |  HEADERS     ::  {H:36}|")if H else None
	print(f"    |  DATA        ::  {d:36}|")if d else None
	print(f"    |  MATCH CODE  ::  {str(mc):36}|")if mc else None
	print(f"    |  IGNORE CODE ::  {str(ic):36}|")if ic else None
	print(f"    |  MATCH LEN   ::  {str(ml):36}|")if ml else None
	print(f"    |  IGNORE LEN  ::  {str(il):36}|")if il else None
	print(f"    |  MATCH WORDS ::  {str(mw):36}|")if mw else None
	print(f"    |  IGNORE WORDS::  {str(iw):36}|")if iw else None
	print(f"    |  MATCH LINE  ::  {str(mli):36}|")if mli else None
	print(f"    |  IGNORE LINE ::  {str(ili):36}|")if ili else None
	print(f"    |  OUTPUT FILE ::  {str(o):36}|")if o else None
	print("    |______________________________________________________|\n\n")
	print(f" {'FUZZ':^48}{'STATUS':^6}{'LENGTH':^10}{'WORDS':^6} {'LINES':^6} {'TIME':^8}")
	print(" ________________________________________________________________________________________")
	print(f"{' ':49}|{' ':^5}|{' ':^8}|{' ':^6}|{' ':^6}|")


def help(msg = None):
	if msg:
		print(msg)
	else:
		logo()
		print ("""
     __________________________________________________________
    |                     |                                    |
    |  -u   --url         |  Target URL (required)         !   |
    |  -w   --wordlist    |  Path to wordlist (required)   !   |
    |                     |                                    |
    |  -t   --threads     |  Number of threads (def. 40)       |
    |  -s   --delay       |  Delay between requests (ex. 0.1)  |
    |                     |                                    |
    |  -p   --payload     |  Payload string (goes after FUZZ)  |
    |  -    --headers     |  Set request header (JSON format)  |
    |  -d   --data        |  Set request data                  |
    |  -m   --method      |  Set request method (def. GET)     |
    |                     |                                    |
    | --mc --match-code   |  Match status code                 |
    |                     |           set 'all' for all codes  |
    | --ic --ignore-code  |  Ignore status code                |
    |                     |                                    |
    | --ml --match-len    |  Match response length or range    |
    |                     |           ex. --ml 10000,11000     |
    | --il --ignore-len   |  Ignore response length or range   |
    |                     |           ex. --il 0,1000          |
    | --mw --match-words  |  Match resp. words count or range  |
    |                     |           ex. --mw 10000,11000     |
    | --iw --ignore-words |  Ignore resp. words count or range |
    |                     |           ex. --iw 0,1000          |
    | --mli --match-lines |  Match resp. lines count or range  |
    |                     |           ex. --mli 10000,11000    |
    | --ili --ignore-lines|  Ignore resp. lines count or range |
    |                     |           ex. --ili 0,1000         |
    |                     |                                    |
"""
+"""    |  -o   --output      |  Write output to json file         |\n"""
+"""    |  -h   --help        |  Show this help message            |
    |_____________________|____________________________________|
""")
	print("""ex.
   fuzzmap -u https://example.com/FUZZ -w directories.txt
   fuzzmap -u https://FUZZ.example.com/ -w subdomains.txt
   fuzzmap -u https://example.com/?id=12FUZZ -w wordlist.txt -p 'javascript:alert()'
   fuzzmap -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminFUZZ'""")

	try:
		sys.exit(0)
	except:
		os._exit(0)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('\nInterrupted')
		save_output(OUTFILE, SETTINGS, OUTDATA)
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
