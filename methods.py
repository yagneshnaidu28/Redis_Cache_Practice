import redis

r=redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)


#set
r.set("user_token", "xyzanc123def456")
#get
token = r.get("user_token")

print(token)
#delete
r.delete("user_token")
