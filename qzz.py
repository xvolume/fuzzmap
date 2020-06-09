#!/usr/bin/python3
import sys, getopt
import workerpool
import urllib3, json
import time
import os.path


WORDLIST = 'wordlists/dirs_common.txt'
THREADS = 40
SLEEP = None
METHOD = 'GET'
HEADER = None
DATA = None
#REQUEST = None
PAYLOAD = ''
URL = None
MATCH_CODE = None
QQQ = None
OUTFILE = None

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
	global QQQ
	global OUTFILE

	try:
		opts, args = getopt.getopt(
			sys.argv[1:],
			"hu:w:t:s:p:H:d:m:o:",
			["help",
			"url=",
			"wordlist=",
			"threads=",
			"delay=",
			"payload=",
			"headers=",
			"data=",
			"method=",
			"output=",
			"match-code="])

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
			elif opt == "--match-code":
				MATCH_CODE = [int(i.strip()) for i in arg.split(',')]
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
			help("Error: method [-u] is required\n")
		else:
			try:
				urllib3.PoolManager().request(METHOD, URL)
			except Exception as e:
				help(f"Error: {str(e)}")

		if 'QQQ' in ( str(URL) + str(HEADER) + str(DATA) ):
			banner(URL, METHOD, WORDLIST, THREADS, SLEEP, PAYLOAD, HEADER, DATA, MATCH_CODE)
			QQQ = [i.strip('\n') for i in open(WORDLIST).readlines()]

			url, header, data = prepare_requests(
				URL,
				QQQ,
				HEADER,
				DATA)

			pool = workerpool.WorkerPool(size=THREADS)
			pool.map(send_request, url, header, data)
			pool.shutdown()
			pool.wait()

			print('\n')
		else:
			help(f"Error: 'QQQ' not found.\n"+
				"ex: -u http://example.com/QQQ (Accepted in url, header and data fields)")

	except Exception as ex:
		help('Error: '+str(ex)+'\n')



def printer(url, r):
	if MATCH_CODE and r.status in MATCH_CODE:
		print(f'\r{url:35}{str(r.status):15}{str(time.time()-start_time)}', end='\n')
	else:
		print(f'\r{url:35}{str(r.status):15}{str(time.time()-start_time)}', end='')


http = urllib3.PoolManager(maxsize = int(THREADS*0.6))
start_time = time.time()

def send_request(url, header, data):
	if SLEEP:
		time.sleep(SLEEP)

	r = http.request(
		METHOD,
		url,
		headers = header,
		body = data,
		timeout = 10)

	printer(url, r)


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


def banner(u, m, w, t, s, p, H, d, mc):
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
	print(f"    |  MATCH CODE  ::  {str(mc):36}|")if mc else None
	print("    |______________________________________________________|\n\n")


def help(msg = None):

	if msg:
		print(msg)
	else:
		print ("""
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
"""
#+"""    |  -o  --output   |  Write output to file                |"""
+"""    |  -h  --help     |  Show this help message              |
    |_________________|______________________________________|
""")
	print("""ex.
   qzz -u https://example.com/QQQ
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
