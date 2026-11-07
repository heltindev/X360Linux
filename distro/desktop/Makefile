# X360Linux v0.3 framebuffer shell (no X11/Wayland/GPU)
CC ?= powerpc-linux-gnu-gcc
CFLAGS ?= -Os -std=c11 -Wall -Wextra -Wno-unused-function -ffunction-sections -fdata-sections
CFLAGS += -mcpu=powerpc -mno-altivec -mno-vsx
LDFLAGS ?= -static -Wl,--gc-sections
LDLIBS ?= -lm

all: x360desk

x360desk: x360desk.c third_party/stb_image.h third_party/font8x8_basic.h
	$(CC) $(CFLAGS) -o $@ x360desk.c $(LDFLAGS) $(LDLIBS)

clean:
	rm -f x360desk
.PHONY: all clean
