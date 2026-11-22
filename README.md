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

O Docker precisa ser integrado ao WSL. Integre-o nas configurações do Docker Desktop.

<img width="1124" height="629" alt="image" src="https://github.com/user-attachments/assets/ebc0ef0a-9e5b-4104-8071-2fcdfd2fa9a4" />


Execute os comandos a seguir no prompt de comando ou no powershell:

```bash
wsl
docker run -it --rm -e DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v /mnt/wslg:/mnt/wslg mic1-sim
``` 
