import redis
import json

class cacheRedis:
    def __init__(self):

        # retrieve the secrets for redis connection
        with open('redisDetails.txt', 'r') as file:
            lines = file.readlines()
            host = lines[0].strip()
            portNum = lines[1].strip()
            pwd = lines[2].strip()

        self.__redisClient = redis.Redis(host=host, port=portNum, username="default", password=pwd)

        if self.__redisClient.ping():
            print("Successfully connected to Redis cloud database!")
        else:
            print("Could not connect!")


    def insertJSONData(self, TTL, key, jsonValue):
        formattedData = json.dumps(jsonValue)
        self.__redisClient.setex(key, TTL, formattedData)
        print(f"Data inserted: {self.__redisClient.get(key)}, TTL (in seconds): {TTL}")

    def checkIfJSONDocExistsAtKey(self, key):
        if self.__redisClient.get(key) is not None:
            print(f"JSON Object: {json.loads(self.__redisClient.get(key))}")
            return True 
        else:
            print(f"No JSON object found at key: '{key}'")
        return False


testCacheRedis = cacheRedis()
testCacheRedis.insertJSONData(20, 'user:1000', {"AthleteID": 5032, "AthleteName": "Alejandro", "SportType": "Run"})
testCacheRedis.checkIfJSONDocExistsAtKey('user:1000')
testCacheRedis.checkIfJSONDocExistsAtKey('user:1001')
