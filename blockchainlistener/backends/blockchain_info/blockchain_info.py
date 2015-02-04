import json
import random
import urllib2
import urllib
import logging
import datetime
import time
import traceback
import secure_request

class BackendServerNotResponding(Exception):
	def __init__(self):
		super(Exception,self).__init__('One of the backend servers is not responding to the request.  Please try again later.')
class BackendServerError(Exception):
	def __init__(self,s):
		super(Exception,self).__init__('BackendServer reported: '+s)
class NoTransactionError(Exception):
	def __init__(self,s):
		super(Exception,self).__init__('Transaction does not exist')

class Context(object):
	def __init__(self):
		self.blockchain_timeout=100000
		self.default_fee=10000  #100 million satoshi/btc * 0.0001 btc = 10000 satoshi
		self.num_blockchain_retries=2

		self.last_request=datetime.datetime.utcnow()
		self.request_persecond=0.428571;
		self.request_quota=5*60.0;
		self.request_time_left=self.request_quota;

		#basically, time_remaining=5 minutes.
		#every time a request takes less than request_persecond, subtract that from the time remaining.
		#every time it takes more, add that to the time remaining (up to 5)
		#if you have no time remaining, delay request_persecond
		#if you have 

	def _request_wait(self):
		self.now_time=datetime.datetime.utcnow()
		self.now_duration=(self.now_time-self.last_request).total_seconds()
		self.request_time_left+=(self.request_persecond-self.now_duration)
		if(self.request_time_left < 0):
			time.sleep(self.request_persecond)
			self._request_wait()
		elif(self.request_time_left > self.request_quota):
			self.request_time_left=self.request_quota


	def make_request(self,*args):
		opener = secure_request.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0'+str(random.randrange(1000000)))]
		self._request_wait()
		try:
			return opener.open(*args).read().strip()
		except Exception,e:
			try:
				p = e.read().strip()
			except: 
				p = e
				raise Exception(p)

	def _bci_request(self,url):
		for x in range(self.num_blockchain_retries):
			try:
				return self.make_request(url)
			except Exception as e:
				if(x==self.num_blockchain_retries-1):
					raise e
				else:
					logging.info("Blockchain request failed.  at Retrying... AT")
				

		#raise BackendServerNotResponding()

	def getaddressinfo(self,address):
		br=json.loads(self._bci_request(url='https://blockchain.info/address/%s?format=json&limit=1' % (address)))
		brc=self._bci_request(url='https://blockchain.info/q/addressbalance/%s?confirmations=6' % (address))
		return {'balance':int(brc),
			'unconfirmed_balance':br['final_balance'], 
			'last_accessed': (0 if len(br['txs']) < 1 else br['txs'][0]['time'])}

	def getaddresslastsenttime(self,address):
		br=json.loads(_bci_request(url='https://blockchain.info/address/%s?format=json&limit=1&filter=1' % (address)))
		return (0 if len(br['txs']) < 1 else br['txs'][0]['time'])

	def send_p(self,btc_private_key,amount,to,fee=None,message=''):
		if(not fee):
			fee=self.default_fee
		br=_bci_request(url='https://blockchain.info/merchant/%s/payment?to=%s&amount=%d&note=%s&fee=%d' % (btc_private_key,to,int(amount),message,int(fee)))
		brj=json.loads(br)
		logging.info("SEND2 RESULT:"+br)
		if('error' in brj):
			raise BackendServerError(brj['error'])
		return brj

	#def send(btc_private_key,amount,to,fee=default_fee,message=''):
	#	br={}
	#	from_addy=utils.private_key2address(btc_private_key)
	#	while('tx_hash' not in br):
	#		try:
	#			br=send_p(btc_private_key,amount,to,fee,message)
	#		except:
	#			br=findtx_tofrom(from_addy,to)
	#
	#	return br

	def sendmany(self,btc_private_key,outputs,fee=None):
		if(not fee):
			fee=self.default_fee
		modded_outputs=dict([(k,int(v)) for k,v in outputs.iteritems()])
		mos=json.dumps(modded_outputs)
		print ("outs: %s" % (mos))
		outstring=urllib.urlencode({'recipients':mos,'fee':int(fee)})
		br=self._bci_request(url='https://blockchain.info/merchant/%s/sendmany?%s' % (btc_private_key,outstring))
		brj=json.loads(br)
		logging.info("SEND2 RESULT:"+br)
		if('error' in brj):
			raise BackendServerError(brj['error'])
		return brj

	def findtx_tofrom(self,from_address,to_address):
		try:
			brc=self._bci_request(url='https://blockchain.info/address/%s?format=json' % (to_address))
			logging.info("FINDTX RESULT:"+brc)
			address_stuff=json.loads(brc)
			for a in address_stuff['txs']:
				if(a['inputs'][0]['prev_out']['addr']==from_address):
					return {'tx_hash':a['hash']}
			return {}
		except:
			return {}	


	def getbalance(self,address,confirmations=0):
		brc=self._bci_request(url='https://blockchain.info/q/addressbalance/%s?confirmations=%s' % (address,str(confirmations)))
		return int(brc)

	def getpublickey(self,address):
		brc=self._bci_request(url='https://blockchain.info/q/pubkeyaddr/%s' % (address))
		if(brc==''):
			return None
		else:
			return brc

	def getblockheight(self):
		brc=self._bci_request(url='https://blockchain.info/q/getblockcount')
		if(brc==''):
			return None
		else:
			return int(brc)

	def getexchangerates(self):
		brc=self._bci_request(url='https://blockchain.info/ticker')
		return json.loads(brc)

	def checkconfirmations(self,txid):
		url='https://blockchain.info/tx/%s?format=json' % (txid)
		p=self._bci_request(url=url)
		if(p.strip()=='Transaction not found'):
			raise NoTransactionError(txid)
		br=json.loads(p)
		if('block_height' in br):
			br2=json.loads(self._bci_request(url='https://blockchain.info/latestblock'))
			txheight=br['block_height']
			return br2['height']-txheight+1
		else:
			return 0

