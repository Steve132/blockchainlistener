import blockchain_info
import json
import time

class Listener(object):
	def __init__(self,block_listener=None,transaction_listener=None,block_confirm_lag=4):
		self.block_listener=block_listener
		self.transaction_listener=transaction_listener
		self.block_confirm_lag=block_confirm_lag
		self.bci=blockchain_info.Context()
	
	def query_blocks(self,previous=0):
		blockheight=None
		while(not blockheight):
			blockheight=self.bci.getblockheight()
		blockheight-=self.block_confirm_lag
		while(previous < blockheight):
			rs=self.bci.make_request("https://blockchain.info/block-height/%d?format=json" % (previous))
			blockrs=json.loads(rs)
			yield blockrs['blocks']
			previous+=1
	
	def stream_blocks(self,previous=0,sleep=60*5):
		for bl in self.query_blocks(previous):
			for b in bl:
				yield b
		time.sleep(sleep)
			
		
