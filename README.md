

# Start OpenTTD Server

```
openttd -D
```

# Start OpenTTD WatchDog client

```
openttd -v null -s null -m null -b null -n 127.0.0.1:3979
```

## use temp config

```
# set to 
openttd -c cfg\private.cfg -v null:ticks=10000000 -s null -m null -x -n "127.0.0.1:3979#255" -d net=
```