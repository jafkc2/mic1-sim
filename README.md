# mic1-sim
Simulador gráfico da microarquitetura MIC-1

## Roadmap

- [x] Montador

-----------------------

Subclasses da classe CPU:

- [ ] DataPath e registradores
- [x] ULA
- [x] Shifter
- [ ] Unidade de controle
- [x] Memória
- [x] Cache

-----------------------

- [x] Interface gráfica


## Como baixar o repositório

#### Requisitos

* Git - Download em https://git-scm.com/. Já vem instalado por padrão na maioria das distribuições linux.

* Token de acesso do Github com acesso a todos os repositórios e permissões (Gere um em https://github.com/settings/personal-access-tokens). Salve o token em um arquivo de texto para ser usado posteriormente.
----------------------------------------


Use o comando a seguir na pasta em que você quer baixar o repositório (Ex: Documentos):

```bash
git clone https://github.com/jafkc2/mic1-sim.git
```

será solicitado o seu nome de usuário do github e o seu token de acesso.


## Dependências do python

* customtkinter

## Docker

#### Build a partir do codigo 

```bash
docker build -t mic1-sim .
``` 

#### Como carregar a partir de uma imagem docker

```bash
docker load -i mic1-sim.tar.gz
``` 

#### Como executar

**No Linux**

```bash
xhost +local:docker
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix mic1-sim
``` 

**No Windows**

```bash
docker run -it --rm -e DISPLAY=:0 -v /tmp/.X11-unix:/tmp/.X11-unix -v /mnt/wslg:/mnt/wslg mic1-sim
``` 
