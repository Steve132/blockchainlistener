from backends.blockchain_info import Listener

if __name__=="__main__":
	l=Listener(block_confirm_lag=5)
	for b in l.stream_blocks(341860):
		print(b)
