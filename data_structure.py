import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)


""" 
#string
r.set("user:101:otp", "987665", ex=300)

otp = r.get("user:101:otp")

print(otp) """


""" 
#List operations basic

r.lpush("tasks", "send_email")
r.lpush("tasks", "generate_report")
r.lpush("tasks", "main")


tasks = r.lrange("tasks", 0,2)

tasks = r.lrange("tasks", 0,-2)

tasks=r.lrange("tasks",0,-1)

task = r.rpop("tasks")

print("Tasks:", tasks)
print("Tasks:", task)
tasks=r.lrange("tasks",0,-1)
print("Tasks:", tasks) """


""" #set - unique values into key 
r.sadd("active_users", "101", "102", "103","104")
# get user members of that key
users = r.smembers("active_users")

print(users)
#delete users from set
r.delete("active_users")   """ 


""" #hash-adding multiple user fields under one key
r.hset("user:101", mapping={
    "name": "John",
    "role": "Admin"
})

user1 = r.hgetall("user:101")
print(user1)

r.hset("user:102", mapping={
    "name": "jimmy",
    "role": "educator"
})
#retrieving one only user
user2=r.hgetall("user:102")
print(user2)
#retrieving all stored info and this is unique hash is unique i mean
for key in r.scan_iter(match="user:*"):
    print(key, r.hgetall(key)) """




""" #sorted set
r.zadd("leaderboard", {
    "John": 100,
    "David": 200
})

ranking_asc = r.zrange(
    "leaderboard", 0, -1, withscores=True
)

ranking_desc = r.zrevrange(
    "leaderboard", 0, -1, withscores=True
)
print("descending",ranking_desc)
print("ascending",ranking_asc) """


""" #stream:store application events
r.xadd("user_events", {
    "user_id": "101",
    "action": "login"
})

events = r.xrange("user_events", "-", "+")
print(events) """