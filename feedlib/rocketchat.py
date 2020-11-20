from rocketchat_API.rocketchat import RocketChat

rocket = RocketChat('fn259', '', server_url='https://uebungen.physik.uni-heidelberg.de/chat/')
print(rocket.me().json())
for channel in rocket.channels_list().json()["channels"]:
    print(channel)
print(rocket.channels_history('ws20-pep1', count=5).json())