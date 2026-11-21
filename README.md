# mic1-sim
Simulador gráfico da microarquitetura MIC-1.


## Roadmap

- [x] Montador
- [x] DataPath e registradores
- [x] ULA
- [x] Shifter
- [x] Unidade de controle
- [x] Memória
- [x] Cache
- [x] CPU 
- [ ] Interface gráfica 

## Como baixar o repositório

#### Requisitos

* Git

----------------------------------------

Use o comando a seguir na pasta em que você quer baixar o repositório (Ex: Documentos):

```bash
git clone https://github.com/jafkc2/mic1-sim.git
```

será solicitado o seu nome de usuário do github e o seu token de acesso.


## Dependências do python

* customtkinter


## Docker

##### Build a partir do codigo 

```bash
docker build -t mic1-sim .
``` 

##### Como carregar a partir de uma imagem docker

```bash
docker load -i mic1-sim.tar.gz
```

------------------
#### Como executar

No Linux:

```bash
xhost +local:docker
sudo docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mic1-sim
``` 

No Windows:

```bash
docker run -it --rm -e DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v /mnt/wslg:/mnt/wslg mic1-sim
``` 
