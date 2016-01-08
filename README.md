# Particleboard

### Stream public events from devices on Particle.io to Hive using Flume HTTP Source

#### Description
Stream public (and/or private) events from a single Particle.io API endpoint into a Flume HTTP Source, then into Hive as ORC format and ultimately on HDFS. You can then convert to Avro using SerDe in Hive and query in Impala. You could also modify the flume agent configuration to sink into other places. By default this will pull real public events from IOT-like devices across the globe into Hadoop.

#### Prerequisites
* Functional Hadoop distro including HDFS, Flume, and Hive at a minimum. I used the [Cloudera Quickstart VM](http://www.cloudera.com/content/www/en-us/downloads/quickstart_vms/5-5.html)
* An API key from [Particle.io](https://www.particle.io). The only way to get one is to buy one of their devices (or ask me!)
* Python (I tested on 2.6.6)

#### Instructions
Download the content on this repo to your Hadoop machine
```
git clone https://github.com/bkvarda/particleboard.git
```
Ensure that Flume and Hive services are deployed and running. For Flume, there are some environmental variables that may need to be set so that the Hive sink and serializers know where some of their required JARs are. In the Cloudera VM, I had to do this:
```
export HIVE_HOME=/usr/lib/hive
export HCAT_HOME=/usr/lib/hive/hcatalog
```
Modify the particleboard.conf to include your Particle API key

You may also need to modify the flume.conf file from this repo. The only ones that should need to be modified, if any, are:
```
a1.sinks.k1.hive.metastore = thrift://127.0.0.1:9083
a1.sinks.k1.hive.database = default
a1.sinks.k1.hive.table = particle
a1.channels.c1.checkpointDir = /home/cloudera/scripts/checkpoint
a1.channels.c1.dataDirs = /home/cloudera/scripts/data
```
Note that the checkpointDir and dataDirs are for channel spill to disk, and these directories should be used only for this purpose

Now create the table in Hive. The format has to be ORC for the Hive sink. The number of buckets is arbitrary and can be changed.
```
DROP TABLE IF EXISTS particle;
CREATE EXTERNAL TABLE particle (
    published_at TIMESTAMP,
    event STRING,
    payload STRING,
    coreid STRING,
    ttl INT)
CLUSTERED BY (published_at) into 3 buckets
STORED AS ORC
LOCATION '/user/cloudera/particle';
```
Once the table is created, you should be ready to go. You can copy the flume.conf content to the Flume config in Cloudera Manager and then start or restart Flume, or you can run it interactively from the terminal like this:
```
flume-ng agent --conf conf --conf-file flume_hive.conf --name a1 -Dflume.root.logger=INFO,console
```
Now in a separate terminal (or from another machine entirely), run the Python script that grabs events from Particle and POSTs them to the (running) Flume HTTP source. First you will need to make sure you have the SSEClient dependency:
```
pip install sseclient
```
Then run the script
```
python particleboard.py
```
On the Python side, you should (by default) see events streaming to the console. On the Flume side, you should see this:
```
16/01/07 22:19:09 INFO instrumentation.MonitoredCounterGroup: Component type: SOURCE, name: r1 started
16/01/07 22:19:23 INFO hive.HiveSink: k1: Creating Writer to Hive end point : {metaStoreUri='thrift://127.0.0.1:9083', database='default', table='particle', partitionVals=[] }
16/01/07 22:19:25 INFO hive.metastore: Trying to connect to metastore with URI thrift://127.0.0.1:9083
16/01/07 22:19:25 INFO hive.metastore: Opened a connection to metastore, current connections: 1
16/01/07 22:19:25 INFO hive.metastore: Connected to metastore.
16/01/07 22:19:26 INFO hive.metastore: Trying to connect to metastore with URI thrift://127.0.0.1:9083
16/01/07 22:19:26 INFO hive.metastore: Opened a connection to metastore, current connections: 2
16/01/07 22:19:26 INFO hive.metastore: Connected to metastore.
16/01/07 22:19:27 INFO hive.HiveWriter: Acquired Transaction batch TxnIds=[2601...2700] on endPoint = {metaStoreUri='thrift://127.0.0.1:9083', database='default', table='particle', partitionVals=[] }
16/01/07 22:19:31 INFO hive.HiveWriter: Committing Txn 2601 on EndPoint: {metaStoreUri='thrift://127.0.0.1:9083', database='default', table='particle', partitionVals=[] }
16/01/07 22:19:58 INFO hive.HiveWriter: Committing Txn 2602 on EndPoint: {metaStoreUri='thrift://127.0.0.1:9083', database='default', table='particle', partitionVals=[] }
16/01/07 22:20:31 INFO hive.HiveWriter: Committing Txn 2603 on EndPoint: {metaStoreUri='thrift://127.0.0.1:9083', database='default', table='particle', partitionVals=[] }
16/01/07 22:21:00 INFO hive.HiveWriter: Committing Txn 2604 on EndPoint: {metaStoreUri='thrift://127.0.0.1:9083', database='default', table='particle', partitionVals=[] }
```
As the transactions are commited, you can query the data in Hive. 
