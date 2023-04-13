import roslibpy


client = roslibpy.Ros(host='10.8.0.1', port=9090)
client.run()

def printScan(f):
    print(len(f['ranges']))

laser_listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
laser_listener.subscribe(printScan)

while True:
    continue