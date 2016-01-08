# Particleboard

### Stream public events from devices on Particle.io to Hive using Flume HTTP Source

#### Description
Stream public (and/or private) events from a single Particle.io API endpoint into a Flume HTTP Source, then into Hive as ORC format and ultimately on HDFS. You can then convert to Avro using SerDe in Hive and query in Impala. You could also modify the flume agent configuration to sink into other sources. By default this will pull real public events from IOT-like devices across the globe into Hadoop.

#### Prerequisites
* Functional Hadoop distro including HDFS, Flume, and Hive at a minimum. I used the [Cloudera Quickstart VM](http://www.cloudera.com/content/www/en-us/downloads/quickstart_vms/5-5.html)
* An API key from [Particle.io](https://www.particle.io). The only way to get one is to buy one of their devices (or ask me!)
* Python (I tested on 2.6.6)

#### Instructions
To come...


