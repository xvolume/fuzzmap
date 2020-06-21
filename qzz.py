#!/usr/bin/python3
import sys, getopt
import workerpool
import urllib3, json
import time
import os.path


WORDLIST = None
THREADS = 40
SLEEP = None
METHOD = 'GET'
HEADER = None
DATA = None
#REQUEST = None
PAYLOAD = ''
URL = None
QQQ = None
OUTFILE = None
MATCH_CODE = [200,204,301,302,307]
IGNORE_CODE = None
MATCH_LEN = None
IGNORE_LEN = None
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
	global QQQ
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
				"ignore-len="])

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
				MATCH_CODE = [int(i.strip()) for i in arg.split(',')]
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
			elif opt in ("-o", "--output"):
				OUTFILE = arg
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
#			urllib3.PoolManager().request(METHOD, URL.replace('QQQ', ''))
#		except Exception as e:
#			help(f"Error: {URL} connection failed\n")

		if 'QQQ' in ( str(URL) + str(HEADER) + str(DATA) ):
			banner(URL, METHOD, WORDLIST, THREADS, SLEEP, PAYLOAD, HEADER,
				DATA, MATCH_CODE, IGNORE_CODE, MATCH_LEN, IGNORE_LEN)

			QQQ = [i.strip('\n') for i in open(WORDLIST).readlines()]

			url, header, data = prepare_requests(URL, QQQ, HEADER, DATA)

			pool = workerpool.WorkerPool(size=THREADS)
			pool.map(send_request, url, header, data)
			pool.shutdown()
			pool.wait()

			print('\n')
		else:
			help(f"Error: 'QQQ' not found.\n"+
				"\tex: -u http://example.com/QQQ (Accepted in url, header and data fields)")

	except Exception as ex:
		help('Error: '+str(ex)+'\n')



def printer(url, r=None):
	progress = str(COUNTER)+'/'+str(len(QQQ))
	url = url.split("//")[1]
	t = time.strftime('%H:%M:%S', time.gmtime(time.time()-start_time))
	len_data = len(r.data) if r else None
	status = r.status if r else None

	if IGNORE_CODE and status and status not in IGNORE_CODE:
		if len_check(len_data):
			print(f'\r {url:48}|{str(status):^5}'+
                        	f'|{str(len_data):^8}| {t:25}', end='\n')
	elif status in MATCH_CODE and IGNORE_CODE is None:
		if len_check(len_data):
			print(f'\r {url:48}|{str(status):^5}'+
				f'|{str(len_data):^8}| {t:25}', end='\n')

	print(f'\r {url[:33]:34}{progress:^14}'+
		f'|{str(status):^5}|{str(len_data):^8}'+
		f'|{t:^10} '+
		f' {"Err: "+str(ERRORS_COUNTER)}', end='')


def len_check(len):
	if MATCH_LEN and IGNORE_LEN is None:
		if type(MATCH_LEN) is list:
			return len in range(MATCH_LEN[0], MATCH_LEN[1])
		else:
			return int(len) == int(MATCH_LEN)
	elif IGNORE_LEN:
		if type(IGNORE_LEN) is list:
			return len not in range(IGNORE_LEN[0], IGNORE_LEN[1])
		else:
			return int(len) != int(IGNORE_LEN)
	else:
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
			retries = False)
		printer(url, r)
	except:
		printer(url)
		ERRORS_COUNTER += 1


def prepare_requests(url, qqq, header=None, data=None):
	u = []
	h = []
	d = []

	for q in qqq:
		if 'QQQ' in url:
			u.append( url.replace('QQQ', q+PAYLOAD) )
		else:
			u.append( url )

		if header:
			if 'QQQ' in header:
				head = header.replace('QQQ', q+PAYLOAD)
			try:
				h.append( json.loads(head) )
			except:
				h.append( None )
		else:
			h.append( header )

		if data:
			d.append( data.replace('QQQ', q+PAYLOAD))
		else:
			d.append( data )


	return u, h, d


def banner(u, m, w, t, s, p, H, d, mc, ic, ml, il):
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
	print(f"    |  HEADER      ::  {H:36}|")if H else None
	print(f"    |  DATA        ::  {d:36}|")if d else None
	print(f"    |  MATCH CODE  ::  {str(mc):36}|")if mc and not ic else None
	print(f"    |  IGNORE CODE ::  {str(ic):36}|")if ic else None
	print(f"    |  MATCH LEN   ::  {str(ml):36}|")if ml and not il else None
	print(f"    |  IGNORE LEN  ::  {str(il):36}|")if il else None
	print("    |______________________________________________________|\n\n")
	print(f" {'URL':^48}{'STATUS':^6}{'LENGTH':^10} {'TIME':^8}")
	print(" __________________________________________________________________________")
	print(f"{' ':49}|{' ':^5}|{' ':^8}|")


def help(msg = None):

	if msg:
		print(msg)
	else:
		print ("""
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
"""
#+"""    |  -o   --output    |  Write output to file              |"""
+"""    |  -h   --help      |  Show this help message            |
    |___________________|____________________________________|
""")
	print("""ex.
   qzz -u https://example.com/QQQ -w directories.txt
   qzz -u https://QQQ.example.com/ -w subdomains.txt
   qzz -u https://example.com/?id=12QQQ -w wordlist.txt -p 'javascript:alert()'
   qzz -u https://example.com -m POST -H '{"Content-type": "text/html"}' -d 'user=adminQQQ'""")

	try:
		sys.exit(0)
	except:
		os._exit(0)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('\nInterrupted')
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
