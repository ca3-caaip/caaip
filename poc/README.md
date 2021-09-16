# CAAJ PoC

## docker
### for start

```
$ docker-compose up -d
```

### for end

```
$ docker-compose down
```

### for remove

```
$ docker-compose down --rmi all --volumes --remove-orphans
```

## how to use

first of all, you need to make setting file.

```
$ cp src/settings.json.orig src/settings.json
$ vim src/settings.json
```

fill parameters in settings.json.

etherscan_key is api key of etherscan
infra_key is api key of infra


### uniswap_to_caaj

```
$ docker-compose exec caaj_poc python /app/uniswap_to_caaj/uniswap_to_caaj.py ethereum_address
```


### caaj_to_cryptact

```
$ docker-compose exec caaj_poc python /app/caaj_to_cryptact/caaj_to_cryptact.py
```
