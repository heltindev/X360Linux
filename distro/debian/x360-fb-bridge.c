/* SPDX-License-Identifier: Apache-2.0
 * X360Linux: copy Xvfb's real X11 desktop to the Xbox 360 framebuffer.
 * Fallback for hardware on which the Xorg fbdev screen probe fails.
 * Uses no GPU acceleration, remote display server, or network connection.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define MAX_INPUT 32
#define XWD_HEADER_WORDS 25
#define XWD_VERSION 7
#define XWD_ZPIXMAP 2

typedef struct _XDisplay XDisplay;
typedef struct {
    void *xlib, *xtst;
    XDisplay *display;
    XDisplay *(*open_display)(const char *);
    int (*close_display)(XDisplay *);
    int (*flush)(XDisplay *);
    int (*fake_key)(XDisplay *, unsigned int, int, unsigned long);
    int (*fake_button)(XDisplay *, unsigned int, int, unsigned long);
    int (*fake_motion)(XDisplay *, int, int, int, unsigned long);
} XInputBridge;
typedef struct {
    int fd, width, height, bpp, stride;
    size_t size;
    uint8_t *mem;
    struct fb_var_screeninfo var;
    struct fb_fix_screeninfo fix;
} Framebuffer;
typedef struct {
    int fd;
    size_t size, image_offset;
    uint8_t *data;
    uint32_t width, height, stride, bpp, order, red_mask, green_mask, blue_mask;
} Xwd;
static volatile sig_atomic_t quitting = 0;
static int input_fds[MAX_INPUT];
static int cursor_x, cursor_y;
static void stop_running(int sig) { (void)sig; quitting = 1; }
static uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];
}
static unsigned channel(uint32_t value, uint32_t mask) {
    if (!mask) return 0;
    unsigned shift = 0;
    while (!(mask & 1U)) { mask >>= 1; shift++; }
    unsigned n = 0, m = mask;
    while (m & 1U) { n++; m >>= 1; }
    uint32_t v = (value >> shift) & mask;
    if (n >= 8) return v >> (n-8);
    return (v * 255U) / ((1U << n) - 1U);
}
static uint32_t channel_to_fb(unsigned val, struct fb_bitfield f) {
    if (!f.length) return 0;
    uint32_t max = f.length >= 31 ? UINT32_MAX : (1U << f.length)-1U;
    uint32_t scaled = f.length >= 8 ? (val << (f.length-8)) : (val * max / 255U);
    return scaled << f.offset;
}
static int open_xwd(const char *path, Xwd *xwd) {
    struct stat st;
    memset(xwd,0,sizeof(*xwd));
    xwd->fd = open(path, O_RDONLY | O_CLOEXEC);
    if (xwd->fd < 0 || fstat(xwd->fd, &st)) return -1;
    if (st.st_size < XWD_HEADER_WORDS*4) return -1;
    xwd->size = (size_t)st.st_size;
    xwd->data = mmap(NULL,xwd->size,PROT_READ,MAP_SHARED,xwd->fd,0);
    if (xwd->data == MAP_FAILED) return -1;
    uint32_t *w = calloc(XWD_HEADER_WORDS,sizeof(uint32_t));
    if (!w) return -1;
    for (int i=0;i<XWD_HEADER_WORDS;i++) w[i]=read_be32(xwd->data+i*4);
    xwd->width=w[4]; xwd->height=w[5]; xwd->order=w[7];
    xwd->bpp=w[11]; xwd->stride=w[12];
    xwd->red_mask=w[14]; xwd->green_mask=w[15]; xwd->blue_mask=w[16];
    /* XWDColor is 12 bytes: pixel(4), RGB(6), flags(1), pad(1). */
    xwd->image_offset=(size_t)w[0]+(size_t)w[19]*12;
    int valid=w[1]==XWD_VERSION && w[2]==XWD_ZPIXMAP &&
        w[0] >= XWD_HEADER_WORDS*4 && xwd->width>=1 && xwd->width<=4096 &&
        xwd->height>=1 && xwd->height<=2160 &&
        xwd->bpp==32 && xwd->stride>=xwd->width*4 &&
        xwd->image_offset<=xwd->size &&
        (uint64_t)xwd->stride*xwd->height<=xwd->size-xwd->image_offset &&
        (xwd->order==0 || xwd->order==1) &&
        (xwd->red_mask && xwd->green_mask && xwd->blue_mask);
    free(w);
    if (!valid) { fprintf(stderr,"X360Linux bridge: unsupported XWD framebuffer\n");return -1; }
    printf("X360LINUX_XWD_OK %ux%u %u-bpp\n",xwd->width,xwd->height,xwd->bpp);
    return 0;
}
static int open_fb(const char *path,Framebuffer *fb) {
    memset(fb,0,sizeof(*fb));
    fb->fd=open(path,O_RDWR|O_CLOEXEC);
    if (fb->fd<0 || ioctl(fb->fd,FBIOGET_FSCREENINFO,&fb->fix) ||
        ioctl(fb->fd,FBIOGET_VSCREENINFO,&fb->var)) {
        perror("X360Linux framebuffer ioctl"); return -1;
    }
    fb->width=(int)fb->var.xres; fb->height=(int)fb->var.yres;
    fb->bpp=(int)fb->var.bits_per_pixel; fb->stride=(int)fb->fix.line_length;
    fb->size=fb->fix.smem_len;
    if (fb->width<=0 || fb->height<=0 || fb->width>4096 || fb->height>2160 ||
        !(fb->bpp==16 || fb->bpp==24 || fb->bpp==32) ||
        fb->stride<(fb->width*(fb->bpp/8)) || !fb->size) {
        fprintf(stderr,"X360Linux: unsupported framebuffer layout\n");return -1;
    }
    fb->mem=mmap(NULL,fb->size,PROT_READ|PROT_WRITE,MAP_SHARED,fb->fd,0);
    if (fb->mem==MAP_FAILED) {perror("framebuffer mmap");return -1;}
    printf("X360LINUX_FB_READY %dx%d depth=%d pitch=%d\n",
           fb->width,fb->height,fb->bpp,fb->stride);
    return 0;
}
static void paint(const Framebuffer *fb,const Xwd *xwd) {
    const uint8_t *src=xwd->data+xwd->image_offset;
    int pixel_bytes=fb->bpp/8;
    unsigned long visible_y=fb->var.yoffset;
    unsigned long visible_x=fb->var.xoffset;
    for (int y=0;y<fb->height;y++) {
        unsigned sy=(unsigned)(((uint64_t)y*xwd->height)/fb->height);
        uint64_t start=(visible_y+(unsigned long)y)*(uint64_t)fb->stride+
                       visible_x*(uint64_t)pixel_bytes;
        if (start+(uint64_t)fb->width*pixel_bytes>fb->size) break;
        uint8_t *dst=fb->mem+start;
        const uint8_t *line=src+(size_t)sy*xwd->stride;
        for (int x=0;x<fb->width;x++) {
            unsigned sx=(unsigned)(((uint64_t)x*xwd->width)/fb->width);
            const uint8_t *p=line+sx*4;
            uint32_t value=xwd->order==0?
                ((uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24)):
                ((uint32_t)p[3]|((uint32_t)p[2]<<8)|((uint32_t)p[1]<<16)|((uint32_t)p[0]<<24));
            uint32_t rgb=channel_to_fb(channel(value,xwd->red_mask),fb->var.red) |
                channel_to_fb(channel(value,xwd->green_mask),fb->var.green) |
                channel_to_fb(channel(value,xwd->blue_mask),fb->var.blue);
            /* Physical Xenon fbdev is big-endian PowerPC; write native words. */
            if (pixel_bytes==4) memcpy(dst+x*4,&rgb,4);
            else if (pixel_bytes==2) {uint16_t small=(uint16_t)rgb;memcpy(dst+x*2,&small,2);}
            else {
                if (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__) {
                    dst[x*3]=(uint8_t)(rgb>>16);dst[x*3+1]=(uint8_t)(rgb>>8);dst[x*3+2]=(uint8_t)rgb;
                } else {
                    dst[x*3]=(uint8_t)rgb;dst[x*3+1]=(uint8_t)(rgb>>8);dst[x*3+2]=(uint8_t)(rgb>>16);
                }
            }
        }
    }
}
static void *load_symbol(void *handle,const char *name) {
    void *sym=dlsym(handle,name);
    if (!sym) fprintf(stderr,"X360Linux missing X symbol %s\n",name);
    return sym;
}
static int setup_xinput(XInputBridge *in) {
    memset(in,0,sizeof(*in));
    in->xlib=dlopen("libX11.so.6",RTLD_LAZY|RTLD_LOCAL);
    in->xtst=dlopen("libXtst.so.6",RTLD_LAZY|RTLD_LOCAL);
    if (!in->xlib || !in->xtst) return -1;
    in->open_display=load_symbol(in->xlib,"XOpenDisplay");
    in->close_display=load_symbol(in->xlib,"XCloseDisplay");
    in->flush=load_symbol(in->xlib,"XFlush");
    in->fake_key=load_symbol(in->xtst,"XTestFakeKeyEvent");
    in->fake_button=load_symbol(in->xtst,"XTestFakeButtonEvent");
    in->fake_motion=load_symbol(in->xtst,"XTestFakeMotionEvent");
    if (!in->open_display || !in->close_display || !in->flush ||
        !in->fake_key || !in->fake_button || !in->fake_motion) return -1;
    in->display=in->open_display(":1");
    return in->display?0:-1;
}
static void scan_inputs(void) {
    for (int i=0;i<MAX_INPUT;i++) {
        if (input_fds[i]>=0) continue;
        char path[64];
        snprintf(path,sizeof(path),"/dev/input/event%d",i);
        input_fds[i]=open(path,O_RDONLY|O_NONBLOCK|O_CLOEXEC);
    }
}
static void handle_input(XInputBridge *in,const Xwd *xwd) {
    if (!in->display) return;
    int dirty=0;
    for (int i=0;i<MAX_INPUT;i++) if(input_fds[i]>=0) {
        struct input_event ev;
        for(int n=0;n<32;n++) {
            ssize_t size=read(input_fds[i],&ev,sizeof(ev));
            if(size!=(ssize_t)sizeof(ev)) {
                if(size<0 && errno!=EAGAIN && errno!=EWOULDBLOCK &&
                   errno!=EINTR) {close(input_fds[i]);input_fds[i]=-1;}
                break;
            }
            if(ev.type==EV_REL && (ev.code==REL_X || ev.code==REL_Y)) {
                if (ev.code==REL_X) cursor_x+=ev.value;
                else cursor_y+=ev.value;
                if(cursor_x<0) cursor_x=0;
                if(cursor_y<0) cursor_y=0;
                if(cursor_x>=(int)xwd->width) cursor_x=(int)xwd->width-1;
                if(cursor_y>=(int)xwd->height) cursor_y=(int)xwd->height-1;
                in->fake_motion(in->display,-1,cursor_x,cursor_y,0);dirty=1;
            } else if(ev.type==EV_KEY) {
                int press=ev.value!=0;
                if(ev.code>=BTN_LEFT && ev.code<=BTN_MIDDLE) {
                    unsigned button=(unsigned)(ev.code-BTN_LEFT+1);
                    in->fake_button(in->display,button,press,0);dirty=1;
                } else if(ev.code==BTN_SOUTH) {
                    in->fake_button(in->display,1,press,0);dirty=1;
                } else if(ev.code==BTN_EAST) {
                    in->fake_key(in->display,9,press,0);dirty=1; /* Escape */
                } else if(ev.code>0 && ev.code<248) {
                    in->fake_key(in->display,(unsigned)ev.code+8,press,0);
                    dirty=1;
                }
            }
        }
    }
    if(dirty) in->flush(in->display);
}
int main(int argc,char **argv) {
    if (argc<2 || argc>4) {
        fprintf(stderr,"usage: %s [--inspect-xwd file | framebuffer xwd-file]\n",argv[0]);
        return 2;
    }
    if(argc==3 && !strcmp(argv[1],"--inspect-xwd")) {
        Xwd xwd;
        if(open_xwd(argv[2],&xwd)) return 1;
        return 0;
    }
    if(argc!=3) return 2;
    signal(SIGTERM,stop_running);signal(SIGINT,stop_running);
    setvbuf(stdout,NULL,_IONBF,0);
    Framebuffer fb;
    if(open_fb(argv[1],&fb)) return 1;
    Xwd xwd;
    int ready=0;
    struct timespec delay={.tv_sec=0,.tv_nsec=125000000};
    for (int i=0;i<80;i++) {
        if(!open_xwd(argv[2],&xwd)) {ready=1;break;}
        nanosleep(&delay,NULL);
    }
    if(!ready) {fprintf(stderr,"X360Linux: Xvfb screen not ready\n");return 1;}
    for(int i=0;i<MAX_INPUT;i++) input_fds[i]=-1;
    XInputBridge in;
    if(setup_xinput(&in)) fprintf(stderr,"X360Linux: XTest input unavailable; display is active\n");
    cursor_x=(int)xwd.width/2; cursor_y=(int)xwd.height/2;
    scan_inputs();
    int tick=0;
    while(!quitting) {
        handle_input(&in,&xwd);
        paint(&fb,&xwd);
        if(++tick%40==0) scan_inputs();
        nanosleep(&delay,NULL);
    }
    if(in.display) in.close_display(in.display);
    munmap(fb.mem,fb.size);
    munmap(xwd.data,xwd.size);
    close(fb.fd);close(xwd.fd);
    for(int i=0;i<MAX_INPUT;i++) if(input_fds[i]>=0) close(input_fds[i]);
    return 0;
}
