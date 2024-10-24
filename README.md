# wano_expert
## Purpose of this repository
This repository contains WaNos (Workflow active Nodes) for the standard usage of Nanomatch scientific software in the Nanoscope environment. Further information on the Nanoscope software and the installation in connection with WaNos are available at the [Nanoscope documentation](https://nanoscope.readthedocs.io).

## Connection to expert WaNo repository
In addition to these standard WaNos, there is a [respository for expert WaNos](https://github.com/NanomatchGmbH/wano_expert) for more refined usage of the OE software package of Nanomatch. In order to use both standard and expert WaNos, clone both repositories and link WaNos from one folder into the other:

``` 
git clone git@github.com:NanomatchGmbH/wano.git
git clone git@github.com:NanomatchGmbH/wano_expert.git 
cd wano
ln -s ../wano_expert/* .
cd ..
```

Further information on usage of the expert WaNos is available at the [Nanomatch documentation](http://docs.nanomatch.de)