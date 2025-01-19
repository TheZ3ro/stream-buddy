class Token:
	def __init__(self, token = None, token360p = None, token480p = None, token720p = None, token1080p = None, expiration = None) -> None:
		self.token = token
		self.token360p = token360p
		self.token480p = token480p
		self.token720p = token720p
		self.token1080p = token1080p
		self.expire = expiration
	
	def __str__(self) -> str:
		t = f"token={self.token}"
		t += f"&token480p={self.token480p}" if self.token480p else ""
		t += f"&token720p={self.token720p}" if self.token720p else ""
		t += f"&expires={self.expire}"
		return t