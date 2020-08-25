#!/usr/bin/python3
import sys, getopt
import workerpool
import urllib3, json
import datetime, time
import os.path
from operator import itemgetter


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
OUTDATA = []
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
PARSE = None

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
	global PARSE

	# For printing in banner
	m_len = ''
	i_len = ''
	m_word = ''
	i_word = ''
	m_line = ''
	i_line = ''

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
				"ignore-lines=",
				"parse="])

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
				m_len = arg.strip()
				if '-' in arg:
					MATCH_LEN = [i for i in range(int(arg.split('-')[0]), int(arg.split('-')[1]))]
				else:
					MATCH_LEN = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("--il", "--ignore-len"):
				i_len = arg.strip()
				if '-' in arg:
					IGNORE_LEN = [i for i in range(int(arg.split('-')[0]), int(arg.split('-')[1]))]
				else:
					IGNORE_LEN = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("--mw", "--match-words"):
				m_word = arg.strip()
				if '-' in arg:
					MATCH_WORDS = [i for i in range(int(arg.split('-')[0]), int(arg.split('-')[1]))]
				else:
					MATCH_WORDS = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("--iw", "--ignore-words"):
				i_word = arg.strip()
				if '-' in arg:
					IGNORE_WORDS = [i for i in range(int(arg.split('-')[0]), int(arg.split('-')[1]))]
				else:
					IGNORE_WORDS = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("--mli", "--match-lines"):
				m_line = arg.strip()
				if '-' in arg:
					MATCH_LINES = [i for i in range(int(arg.split('-')[0]), int(arg.split('-')[1]))]
				else:
					MATCH_LINES = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("--ili", "--ignore-lines"):
				i_line = arg.strip()
				if '-' in arg:
					IGNORE_LINES = [i for i in range(int(arg.split('-')[0]), int(arg.split('-')[1]))]
				else:
					IGNORE_LINES = [int(i.strip()) for i in arg.split(',')]
			elif opt in ("-o", "--output"):
				OUTFILE = arg.strip()
			elif opt == "--parse":
				PARSE = arg.strip()

#			elif opt == "-r":
#				if os.path.isfile(arg):
#					f = open(arg)
#					REQUEST = f.read()
#					f.close()
			else:
				help( f"Error: [{opt}] unhandled option\n" )


		if PARSE is not None:
			if os.path.exists(PARSE):
				parser(PARSE, MATCH_CODE)
			else:
				help( f'Error: file {PARSE} not found\n' )

		elif URL is not None and WORDLIST is not None:
			if 'FUZZ' in ( str(URL) + str(HEADER) + str(DATA) ):
				default_MATCH_CODES = MATCH_CODE

				if MATCH_CODE is None and IGNORE_CODE is None:
					default_MATCH_CODES = [200,204,301,302,307]

				banner(URL, METHOD, WORDLIST, THREADS, SLEEP, PAYLOAD, HEADER,
					DATA, default_MATCH_CODES, IGNORE_CODE, m_len, i_len,
					m_word, i_word, m_line, i_line, OUTFILE)

				FUZZ = [i.strip('\n') for i in open(WORDLIST).readlines()]

				url, header, data, query = prepare_requests(URL, FUZZ, HEADER, DATA)

				pool = workerpool.WorkerPool(size=THREADS)
				pool.map(send_request, url, header, data, query)
				pool.shutdown()
				pool.wait()

				save_output(OUTFILE, SETTINGS, OUTDATA)

				print('\n')
			else:
				help(f"Error: 'FUZZ' not found.\n"+
					"Example: -u http://example.com/FUZZ (Accepted in url, header and data fields)")
		else:
			help("Error: missing required params\n")

	except Exception as ex:
		help('Error: '+str(ex)+'\n')


def parser(file_to_parse, by_code):
	json_data = None

	with open(file_to_parse, 'r') as f:
		json_data = json.load(f)

	json_settings = json_data['settings']

	target =        json_settings['target']
	method =        json_settings['method']
	wordlist =      json_settings['wordlist']
	threads =       json_settings['threads']
	delay =         json_settings['delay']        if 'delay' in json_settings else None
	payload =       json_settings['payload']      if 'payload' in json_settings else None
	headers =       json_settings['headers']      if 'headers' in json_settings else None
	data =          json_settings['data']         if 'data' in json_settings else None
	match_code =    json_settings['match_code']   if 'match_code' in json_settings else None
	ignore_code =   json_settings['ignore_code']  if 'ignore_code' in json_settings else None
	match_len =     json_settings['match_len']    if 'match_len' in json_settings else None
	ignore_len =    json_settings['ignore_len']   if 'ignore_len' in json_settings else None
	match_words =   json_settings['match_words']  if 'match_words' in json_settings else None
	ignore_words =  json_settings['ignore_words'] if 'ignore_words' in json_settings else None
	match_lines =   json_settings['match_lines']  if 'match_lines' in json_settings else None
	ignore_lines =  json_settings['ignore_lines'] if 'ignore_lines' in json_settings else None
	output_file =   json_settings['output_file']  if 'output_file' in json_settings else None
	is_parse =      True

	banner( target, method, wordlist, threads, delay, payload,
		headers, data, match_code, ignore_code, match_len, ignore_len,
		match_words, ignore_words, match_lines, ignore_lines, output_file, is_parse )

	print(f'{"[PARSER]":^62}\n')

	if by_code is not None:
		print(f" {'FUZZ':^40}{'STATUS':^6}{'LENGTH':^10}{'WORDS':^6} {'LINES':^6} {'TIME':^10}{'REDIRECT':^20}")
		print("_"*101)
		print(f"{' ':41}|{' ':^5}|{' ':^8}|{' ':^6}|{' ':^6}|{' ':^10}|")
	else:
		print(f"{'STATUS CODE':^15} {'COUNT':^9} {'LENGTH RANGE':^19}")
		print("_"*45)
		print(f"{' ':^15}|{' ':^9}|{' ':^19}|")


	#Sorting
	json_data['results'] = sorted(json_data['results'], key = itemgetter('length', 'words', 'lines'))
	check_code = []

	for result in json_data['results']:

		if by_code is None:
			if result['status'] not in check_code:
				counter = 0
				lens = []

				for i in json_data['results']:
					if i['status'] == result['status']:
						counter += 1
						lens.append( int(i['length']) )

				len_range = f"{str( min(lens) ):>8} - {str( max(lens) ):<8}"
				check_code.append( result['status'] )

				print( f'{result["status"]:^15}|{str(counter):^9}|{len_range:^19}|' )

		else:
			fuzz =       result['FUZZ']
			status =     result['status']
			len_data =   result['length']
			words_data = result['words']
			lines_data = result['lines']
			t =          result['time']
			redirect =   result['redirect']

			if 'all' == by_code or result['status'] in by_code:
				print( f' {fuzz:40}|{str( status ):^5}'+
					f'|{str( len_data ):^8}|{str( words_data ):^6}'+
					f'|{str( lines_data ):^6}|{t:^10}| {str( redirect ):20}', end='\n' )


def output(url, fuzz, redirect, status, length, words, lines, time):
	global OUTDATA

	OUTDATA.append({
		'FUZZ':     fuzz,
		'url':      url,
		'redirect': redirect,
		'status':   status,
		'length':   length,
		'words':    words,
		'lines':    lines,
		'time':     time
	})


def save_output(file, settings, results):
	date = datetime.datetime.now().strftime( "%d/%m/%y %H:%M" )

	if file and settings and results:

		data = {
			'settings': settings,
			'results': results,
			'date': date
		}
		data_len = str( len(str(data)) )

		try:
			with open(file, 'w') as f:
				json.dump(data, f)
			print( f'\n\nOutput saved to {file}\nTotal: {data_len} bytes' )

		except Exception as e:
			print( '\n'+str(e) )


def printer(url, fuzz, r=None):

	progress   =  str(COUNTER)+'/'+str( len(FUZZ) )
	t          =  time.strftime( '%H:%M:%S', time.gmtime(time.time()-start_time) )
	len_data   =  len(r.data) if r else None
	words_data =  len( str(r.data).split(' ') ) if r else None
	lines_data =  len( str(r.data).split('\n') ) if r else None
	status     =  r.status if r else None
	redirect   =  r.get_redirect_location() if r and r.get_redirect_location() else None

	#Clear previous line
	sys.stdout.write('\x1b[2K')


	if MATCH_CODE and str(MATCH_CODE) == 'all' and IGNORE_CODE is None or\
		MATCH_CODE and str(MATCH_CODE) == 'all' and IGNORE_CODE and status not in IGNORE_CODE:

		if len_check( MATCH_LEN, IGNORE_LEN, len_data ) and\
			len_check( MATCH_WORDS, IGNORE_WORDS, words_data ) and\
			len_check( MATCH_LINES, IGNORE_LINES, lines_data ):
			if OUTFILE and status and len_data and words_data and lines_data:
				output( url, fuzz, redirect, status, len_data, words_data, lines_data, t )

			print( f'\r {fuzz:40}|{str(status):^5}'+
				f'|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}|{t:^10}|', end='\n' )


	elif MATCH_CODE and str(MATCH_CODE) != 'all' and status in MATCH_CODE and IGNORE_CODE is None or\
		IGNORE_CODE and status not in IGNORE_CODE and MATCH_CODE is None or\
		MATCH_CODE and IGNORE_CODE and str(MATCH_CODE) != 'all' and status in MATCH_CODE and status not in IGNORE_CODE:

		if len_check( MATCH_LEN, IGNORE_LEN, len_data ) and\
			len_check( MATCH_WORDS, IGNORE_WORDS, words_data ) and\
			len_check( MATCH_LINES, IGNORE_LINES, lines_data ):
			if OUTFILE and status and len_data and words_data and lines_data:
				output( url, fuzz, redirect, status, len_data, words_data, lines_data, t )

			print( f'\r {fuzz:40}|{str(status):^5}'+
				f'|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}|{t:^10}|', end='\n' )


	elif MATCH_CODE is None and IGNORE_CODE is None:
		if status in [ 200, 204, 301, 302, 307 ]:

			if len_check( MATCH_LEN, IGNORE_LEN, len_data ) and\
				len_check( MATCH_WORDS, IGNORE_WORDS, words_data ) and\
				len_check( MATCH_LINES, IGNORE_LINES, lines_data ):
				if OUTFILE and status and len_data and words_data and lines_data:
					output( url, fuzz, redirect, status, len_data, words_data, lines_data, t )

				print( f'\r {fuzz:40}|{str(status):^5}'+
					f'|{str(len_data):^8}|{str(words_data):^6}|{str(lines_data):^6}|{t:^10}|', end='\n' )


	print( f'\r {fuzz[:26]:26}{progress:^14}'+
		f'/{str(status):^5}/{str(len_data):^8}/{str(words_data):^6}/{str(lines_data):^6}'+
		f'/{t:^10}'+
		f'/{" Err: "+str(ERRORS_COUNTER)}', end='' )


def len_check(match, ignore, len):
	try:
		if match and ignore is None:
			return int(len) in match

		elif ignore and match is None:
			return int(len) not in ignore

		elif match and ignore:
			return int(len) in match and int(len) not in ignore

		elif match is None and ignore is None:
			return True
	except:
		return False


http = urllib3.PoolManager(maxsize = int(THREADS*0.6))
start_time = time.time()

def send_request(url, header, data, query):
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
		printer(url, query, r)
	except:
		printer(url, query)
		ERRORS_COUNTER += 1


def prepare_requests(url, FUZZ, header=None, data=None):
	u = []
	h = []
	d = []
	f = []

	for q in FUZZ:
		f.append( q )

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


	return u, h, d, f


def logo():
	print("""
                 __ ___________  ____________
   )         __  ___  ____/_  / / /__  /__  /__________________
  /(  )         ___  /_  __  / / /__  /__  /__     \  __ `  __ \\
 (  )( )  )      _  __/   / /_/ /__  /__  /__  / / / /_/ / /_/ /
( \( (  )/ )___  /_/   ___\____/  /____/____/_/_/_/\__,_/ .___/
                                                       __/

                      by @xvolume/@avolume
""")


def banner(u, m, w, t, s, p, H, d, mc, ic, ml, il, mw, iw, mli, ili, o, is_parse=False):
	global SETTINGS

	SETTINGS = {
		'target':   u,
		'method':   m,
		'wordlist': w,
		'threads':  t
	}

	SETTINGS.update( { 'delay':        s } )   if s else None
	SETTINGS.update( { 'payload':      p } )   if p else None
	SETTINGS.update( { 'headers':      H } )   if H else None
	SETTINGS.update( { 'data':         d } )   if d else None
	SETTINGS.update( { 'match_code':   mc } )  if mc else None
	SETTINGS.update( { 'ignore_code':  ic } )  if ic else None
	SETTINGS.update( { 'match_len':    ml } )  if ml else None
	SETTINGS.update( { 'ignore_len':   il } )  if il else None
	SETTINGS.update( { 'match_words':  mw } )  if mw else None
	SETTINGS.update( { 'ignore_words': iw } )  if iw else None
	SETTINGS.update( { 'match_lines':  mli } ) if mli else None
	SETTINGS.update( { 'ignore_lines': ili } ) if ili else None
	SETTINGS.update( { 'output_file':  o } )   if o else None

	logo()

	print(f"""
                            Settings
     ______________________________________________________
    |                                                      |
    |  URL         ::  {u:36}|
    |  METHOD      ::  {m:36}|
    |  WORDLIST    ::  {w:36}|
    |  THREADS     ::  {str(t):36}|""")
	print(f"    |  DELAY       ::  {str(s):36}|")   if s else None
	print(f"    |  PAYLOAD     ::  {p:36}|")        if p else None
	print(f"    |  HEADERS     ::  {H:36}|")        if H else None
	print(f"    |  DATA        ::  {d:36}|")        if d else None
	print(f"    |  MATCH CODE  ::  {str(mc):36}|")  if mc else None
	print(f"    |  IGNORE CODE ::  {str(ic):36}|")  if ic else None
	print(f"    |  MATCH LEN   ::  {str(ml):36}|")  if ml else None
	print(f"    |  IGNORE LEN  ::  {str(il):36}|")  if il else None
	print(f"    |  MATCH WORDS ::  {str(mw):36}|")  if mw else None
	print(f"    |  IGNORE WORDS::  {str(iw):36}|")  if iw else None
	print(f"    |  MATCH LINE  ::  {str(mli):36}|") if mli else None
	print(f"    |  IGNORE LINE ::  {str(ili):36}|") if ili else None
	print(f"    |  OUTPUT FILE ::  {str(o):36}|")   if o else None
	print("    |______________________________________________________|\n\n")

	if not is_parse:
		print(f" {'FUZZ':^40}{'STATUS':^6}{'LENGTH':^10}{'WORDS':^6} {'LINES':^6} {'TIME':^10}")
		print("_"*81)
		print(f"{' ':41}|{' ':^5}|{' ':^8}|{' ':^6}|{' ':^6}|{' ':^10}|")


def help(msg = None):
	if msg:
		print(msg)
	else:
		logo()
		print ("""
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
"""
+"""    |   -o   --output     |  Write output to file (JSON)       |\n"""
+"""    |   -h   --help       |  Show this help message            |
    |_____________________|____________________________________|
""")
	print("""Examples:
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
