#!/usr/bin/env python3
"""Create Xbox 360 X360OS native kernel boot image without old embedded Ubuntu."""
from pathlib import Path
import hashlib
import runpy
import sys

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as file:
        for chunk in iter(lambda:file.read(4*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main(original, own_initramfs, output_dir):
    here=Path(__file__).resolve().parent
    out=Path(output_dir)
    assert not out.exists(), "STOP: Never overwrite an existing build directory"
    assert Path(original).is_file() and Path(own_initramfs).is_file()
    out.mkdir(parents=True)
    patch=runpy.run_path(str(here/"patch-embedded-kernel.py"))["replace"]
    patch(original,own_initramfs,out/"vmlinux")
    # Important: NO separate initrd. The Free60 kernel's .init.ramfs is now
    # replaced in-place, and the original ELF layout/entry is preserved.
    (out/"kboot.conf").write_bytes(
        b"#KBOOTCONFIG\n"
        b"; X360OS v9 native boot: custom embedded initramfs, no Casper\n"
        b"; Unchanged Xenon ELF headers, native PowerPC rootfs within vmlinux\n"
        b"default=X360OS\n"
        b"timeout=0\n"
        b'X360OS="uda:/vmlinux rdinit=/init console=tty0 video=xenonfb panic=0 maxcpus=3 loglevel=7"\n')
    (out/"TESTE-PTBR.txt").write_text(
        "X360OS v9 - BOOT NATIVO SEM UBUNTU (TESTE)\n"
        "A imagem anterior NAO carregou; esta variante corrige o initramfs interno.\n"
        "Descobrimos que o kernel Free60 continha um arquivo LZMA EMBUTIDO\n"
        "com 15,9 MB de arquivos antigos Ubuntu/Casper. A v9 SUBSTITUI ESSE\n"
        "CONTEUDO por arquivos X360OS nativos, sem installer ou root Ubuntu.\n"
        "O arquivo vmlinux foi regravado SOMENTE na secao .init.ramfs.\n"
        "O restante do ELF, enderecos e carregamento XeLL permanecem iguais.\n"
        "Nao precisa initrd externo, filesystem.squashfs nem casper-rw.\n"
        "Sua sessao grafica X360OS abre automaticamente caso o boot funcione.\n"
        "As mensagens de boot vao para a TV (console=tty0, sem serial).\n"
        "VIDEO/BOOT NO XBOX REAL: AINDA NAO VALIDADO. PODE FALHAR.\n"
        "Teste em OUTRO pendrive FAT32, copie os arquivos para a RAIZ do USB.\n"
        "Inicie via Eject / XeLL. Se falhar, fotografe a ULTIMA linha visivel\n"
        "e informe se a tela fica no XeLL ou chega a imprimir 'X360OS NATIVE'.\n"
        "NAO altere a NAND, o HDD interno ou o pendrive antigo.\n",encoding="utf-8")
    (out/"READ-ME-FIRST.txt").write_text(
        "X360OS v9 embedded Free60 initramfs experiment (Ubuntu-free guest).\n"
        "Unlike v8, v9 REMOVES the old embedded Ubuntu/Casper initramfs.\n"
        "Kernel is the proven XeLL PPC ELF layout with its .init.ramfs\n"
        "section replaced in-place with native PowerPC BusyBox/musl/X360OS C.\n"
        "No external initrd, GNOME, Python, Ubuntu, Casper, Xorg or installer.\n"
        "Static host/QEMU tests do NOT prove real Xbox boot or framebuffer!\n"
        "For first test copy all files to a SEPARATE FAT32 USB root and Eject.\n"
        "Video console boot logs: tty0. No NAND, HDD or old USB changes.\n",encoding="utf-8")
    (out/"SHA256SUMS.txt").write_text(
        "".join(f"{sha(out/name)}  {name}\n" for name in
                ("vmlinux","kboot.conf","TESTE-PTBR.txt","READ-ME-FIRST.txt")),
        encoding="ascii")
    print("X360OS_V9_NATIVE_BOOT_IMAGE_GENERATED",out)
    for p in out.iterdir(): print(p.name,p.stat().st_size)

if __name__=="__main__":
    assert len(sys.argv)==4,"usage: build-v9.py ORIGINAL_FREE60_VMLINUX V8_NATIVE_INITRD NEW_EMPTY_DIR"
    main(sys.argv[1],sys.argv[2],sys.argv[3])
