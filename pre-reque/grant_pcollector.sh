#!/bin/bash

usuario="pcollector"
senha="*EEA613482E2033A290D61215E3DBDA260731B9C7" #run4all

QUERY="GRANT PROCESS, REPLICATION CLIENT ON *.* TO '${usuario}'@'127.0.0.1' IDENTIFIED BY PASSWORD '${senha}';
       GRANT PROCESS, REPLICATION CLIENT ON *.* TO '${usuario}'@'localhost' IDENTIFIED BY PASSWORD '${senha}';
       GRANT SELECT ON *.* TO '${usuario}'@'localhost';
       GRANT SELECT ON *.* TO '${usuario}'@'127.0.0.1';
       update mysql.user set Password='${senha}' where User='${usuario}'; 
       FLUSH privileges;"


SERVERS="dhc-zeus dhc-athena  dhc-artemis  dhc-hera dhc-hercules dhc-hestia dhc-palas dhc-cratos dhc-teseu dhc-tenebroso dhc-destemido dhc-tetis dhc-temis dhc-demeterd dhc-demeteri dhc-apolo dhc-urano_ dhc-urano dhc-netuno dhc-helio dhc-afrodite_ dhc-afrodite dhc-hefestos dhc-thor dhc-edipo dhc-ulissesd dhc-ulissesi dhc-hermes dhc-cronos dhc-aquiles dhc-aquilesd dhc-aquilesi dhc-tales dhc-pitagoras dhc-orion dhc-taurus dhc-gaia dhc-gravata"

for i in $SERVERS; 
do
	echo "Servidor $i"
	mysql -u carlos.smanioto -p'carlos123' -h ${i}.servers -e"$QUERY"
done
