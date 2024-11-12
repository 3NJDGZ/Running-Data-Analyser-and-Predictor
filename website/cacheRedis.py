import redis

class cacheRedis:
    def __init__(self):

        # retrieve the secrets for redis connection
        with open('redisDetails.txt', 'r') as file:
            lines = file.readlines()
            host = lines[0].strip()
            portNum = lines[1].strip()
            pwd = lines[2].strip()

        self.__r = redis.Redis(host=host, port=portNum, username="default", password=pwd)
        print(self.__r.ping())

        #self.__r.set("TestKey1", "TestKeyValue1")
testCacheRedis = cacheRedis()
