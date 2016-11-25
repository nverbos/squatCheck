import httplib
conn = httplib.HTTPConnection("127.0.0.1:5000")

body = """{
	"vibrationEvent": {
		"source": "2",
		"timeStamp": "1478714159"
	}
}"""
conn.request("POST", "/addVibrationData",  body)
res = conn.getresponse()
print res.status, res.reason