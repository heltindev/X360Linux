# X360Linux — Como iniciar no Xbox 360

**Estado: experimental.** O XeLL iniciou o kernel antigo no Corona Phison RGH, mas ele entrou no Ubuntu Live/instalador. O novo boot direto para a imagem ext4 ainda precisa ser testado no Xbox.

## A tela "XeLL Main Menu. Please choose from"

O titulo em ingles faz parte do programa **XeLL** instalado no console e nao pode ser alterado apenas com `kboot.conf`. Personalizamos os nomes das opcoes:

- **0 — ABRIR O LINUX JA INSTALADO:** testa o novo `x360linux.elf`, que tem o initramfs embutido e procura `distros/ubuntu-x360/rootfs.ext4`. **Nao foi confirmado no console.**
- **1 — VER ERROS DO LINUX:** mesmo boot, mas com textos de diagnostico na tela. **Escolha este primeiro se quiser ajudar a identificar o problema.**
- **2 — SISTEMA ANTIGO - ABRE INSTALADOR:** kernel `vmlinux` original que voce ja conseguiu abrir. **Esta opcao usa Ubuntu Live/Casper e NAO testa o Linux instalado.**

## Teste correto

1. Desligue o console completamente.
2. Conecte o pen drive FAT32 `X360LINUX`.
3. Ligue o Xbox 360 usando o botao **Eject** para iniciar o XeLL ja instalado.
4. Na lista, use **direcional do controle e botao A** para selecionar a **opcao 1 (VER ERROS DO LINUX)**.
5. Se aparecer erro, fotografe a **ultima tela completa**, especialmente linhas com `X360Linux:`, `Kernel panic`, `init`, `USB` ou `ext4`. Se conseguir entrar no desktop, teste mouse, teclado e reinicializacao.
6. Depois que a opcao 1 funcionar, teste a **opcao 0** para a inicializacao mais limpa.

**Nao escolha a opcao 2 esperando entrar no Linux ja instalado.** Ela serve apenas para comprovar que o boot antigo funciona.

## O que foi realmente corrigido no computador

O kernel antigo contem um initramfs antigo do Casper/Ubuntu. Para contornar a falha do carregamento externo da nova imagem `initrd.gz`, criamos um **novo `x360linux.elf`** com o initramfs PowerPC do projeto incorporado. O `vmlinux` antigo continua intacto para recuperacao. A nova imagem preinstalada fica em `distros/ubuntu-x360/rootfs.ext4` (3 GiB), sem instalador.

Os arquivos foram validados no Windows/WSL antes de copiar para o USB. O sucesso da inicializacao no hardware **ainda nao foi demonstrado**.

## Seguranca

Nenhum comando deve atualizar a NAND ou gravar o HD interno. **Nao use arquivos `updflash.bin` ou `updxell.bin`.** O `default.xex` do Aurora continua com tela preta neste Corona Phison e nao deve ser tratado como funcional.

O backup dos arquivos anteriores do USB ficou em:
`PEN DRIVE\work\ARCHIVE-LEGACY\USB-E-BEFORE-EMBEDDED-INITRAMFS`

O backup e os scripts de desenvolvimento ficam no PC, nao no pendrive.
