# Neutron

Neutron is a distributed air quality testing platform that can be expanded to support as many nodes as necessary to test even the largest buildings or homes.

### Hardware

Initial hardware will be based on a Raspberry Pi with BME680 and a PMS5003 Pariculate Matter sensor. I will need to build a 3D printed case for a handful of these systems to hold the Pi and sensors. The setup will be POE powered and I will need to setup a VPN tunnel to connect to it from my laptop from anywhere. 

The main unit will be a Raspberry Pi as well, but will need to hold the POE switch with it in the Pelican case.

### Software

Main Node (known as Neutron) will run containerized versions of InfluxDB and Grafana, as well as a configuration web interface to configure the various nodes on network. 

Remove Nodes (known as Neutrinos) will run a Python application to scrape data from the sensors and then write them to the database.

### Dashboard

Dashboard will be automatically loaded using a helper container that will run against the DB once it's instantiated.

### TODO

* [ ] Create InfluxDB dashboard, export JSON
* [ ] Create helper container to load JSON dashboard and other items using IDB API
* [ ] API Keys for IDB should be at customer level, not neutrino
* [ ] New customer workflow needs to create IDB API key and IDB bucket, remove API Key process from neutrinos - OR - keep the concept of customer key vs default key, so data is never lost if not connected via customer key
* [ ] InfluxDB should monitor the Neutrinos and Containers running on them using Telegraf
* [ ] Keep in mind that you should be able to run Neutron anywhere, not just in a SaaS manner (off-grid on Shiraz's RV for example)

### Notes

* If data storage for InfluxDB fails or gets wiped out somehow, `.env` needs updated with new Token for `kg's Token` and the new default organizations `['orgs']['id']`: `curl --request GET https://neutrondb.kilo.green/api/v2/orgs --header "Authorization: Token INSERTKGTOKENHERE"`

##### REFS

* https://docs.influxdata.com/influxdb/v2.0/api/#tag/Dashboards