# X360Linux — iniciar automaticamente pelo Eject

O pendrive FAT32 foi configurado com default=ABRIR O LINUX JA INSTALADO
e timeout=0. O arquivo experimental x360linux.elf sera selecionado
automaticamente pelo XeLL para tentar iniciar a imagem Ubuntu ja
descompactada em distros/ubuntu-x360/rootfs.ext4 (3 GiB).

## Como testar

1. Ejete o pendrive com seguranca no Windows.
2. Conecte o USB ao Xbox 360 desligado.
3. Ligue o Xbox pelo botao fisico Eject.
4. O XeLL tenta abrir o Ubuntu automaticamente, sem escolher uma opcao.

O titulo em ingles XeLL Main Menu ainda pode aparecer brevemente,
pois vem do proprio XeLL instalado no Xbox. Editar kboot.conf elimina
a espera, mas nao remove as mensagens internas do XeLL.

## Se a inicializacao falhar

O novo x360linux.elf AINDA NAO chegou comprovadamente ao desktop no
Xbox 360 Corona Phison. Para recuperar o menu com 25 segundos e opcoes
de diagnostico, restaure no USB com o nome kboot.conf o arquivo:

PEN DRIVE/work/X360Linux-v05-source/XELL-MENU-MANUAL-BACKUP-2026-11-08.conf

Esse menu permite escolher o boot de teste com mensagens de erro e o
kernel antigo vmlinux, que entra no Ubuntu Live/instalador em vez da
imagem ext4 preinstalada.

O Linux ja foi preparado no arquivo ext4 sem instalador no console;
o que ainda falta comprovar e o kernel conseguir abri-lo no hardware.
Nenhuma NAND ou HDD interno do Xbox foi alterado.
