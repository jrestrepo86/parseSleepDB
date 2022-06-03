# parseSleepDataBase


## Paquetes
* pandas_read_xml
* pyedflib
* pandas
* numpy
* matplotlib
* scipy

## Correcciones en edfs

los edfs vienen con errores en la fecha, hay que correr un archivo escrito en
ruby (rewrite_signal_date.rb) que está en la carpeta de edfs. Hay que instalar
las dependencias de ruby 
* gem install edfize --no-document
* gem install colorize --no-document
* correr el archivo ruby rewrite_signal_date.rb
