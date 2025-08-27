from urllib.parse import urlparse, parse_qs

class Token:
	def __init__(self, token = None, token360p = None, token480p = None, token720p = None, token1080p = None, expiration = None, fhd = False, base_url = None) -> None:
		if base_url is not None:
			q = urlparse(base_url).query
			params = parse_qs(q)
			for key in ["t", "token", "referer", "expires", "canPlayFHD"]:
				if key in params:
					params.pop(key)
			self.params = params
		self.token = token
		self.token360p = token360p
		self.token480p = token480p
		self.token720p = token720p
		self.token1080p = token1080p
		self.expire = expiration
		self.fhd = 1 if fhd else 0
	
	def __str__(self) -> str:
		t = f"token={self.token}"
		t += f"&token480p={self.token480p}" if self.token480p else ""
		t += f"&token720p={self.token720p}" if self.token720p else ""
		t += f"&expires={self.expire}"
		t += f"&h={self.fhd}"
		return t