/* SPDX-License-Identifier: GPL-2.0-only
 * X360Linux Desk v0.3: native Linux framebuffer media shell for Xbox 360.
 * Images: stb_image (public-domain/MIT) and RGB video: X36V (no audio).
 * No X11/DRM/GPU required; console framebuffer and /dev/input/event* only.
 * Not guaranteed to work on real Xenon hardware until a console test.
 */
#define _DEFAULT_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>
#define STBI_ONLY_JPEG
#define STBI_ONLY_PNG
#define STBI_ONLY_BMP
#define STBI_ONLY_PNM
#define STBI_NO_HDR
#define STBI_NO_LINEAR
#define STB_IMAGE_IMPLEMENTATION
#include "third_party/stb_image.h"
#include "third_party/font8x8_basic.h"

#define MAX_MEDIA 80
#define LIMIT_PIXELS 5000000
#define SCREEN_BG 0x0c121b
#define ACCENT 0x40d778
#define TEXT 0xeef5f4
#define MUTED 0x96a8b4

typedef struct {char file[512];char label[128];} Media;
typedef struct {
 int fd; uint8_t *mem;size_t memsize;struct fb_var_screeninfo var;
 struct fb_fix_screeninfo fix;int w,h,bpp;
} Display;
static Display g;
static Media list[MAX_MEDIA];
static int nfiles,selected,tab,mode,should_exit,gamepad_fd=-1,keyboard_fd=-1;
static int mx,my,ax,ay,dx,dy;
static uint8_t buttons[KEY_MAX+1];

static int limit(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
static uint32_t scalechan(int v,struct fb_bitfield chan){
 if(!chan.length)return 0;
 unsigned n=chan.length>16?16:chan.length;
 return (uint32_t)((v*((1u<<n)-1)+127)/255)<<chan.offset;
}
static void pixel(int x,int y,uint32_t color){
 if(x<0||y<0||x>=g.w||y>=g.h)return;
 size_t off=(size_t)(y+g.var.yoffset)*g.fix.line_length+
  (size_t)(x+g.var.xoffset)*(unsigned)g.bpp;
 if(off+(size_t)g.bpp>g.memsize)return;
 uint32_t v=scalechan((color>>16)&255,g.var.red)|
  scalechan((color>>8)&255,g.var.green)|
  scalechan(color&255,g.var.blue);
 if(g.bpp==4)memcpy(g.mem+off,&v,4);
 else if(g.bpp==2){uint16_t s=(uint16_t)v;memcpy(g.mem+off,&s,2);}
 else if(g.bpp==3){
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
  g.mem[off]=(v>>16)&255;g.mem[off+1]=(v>>8)&255;g.mem[off+2]=v&255;
#else
  g.mem[off]=v&255;g.mem[off+1]=(v>>8)&255;g.mem[off+2]=(v>>16)&255;
#endif
 }
}
static void rect(int x,int y,int w,int h,uint32_t color){
 int x0=limit(x,0,g.w),y0=limit(y,0,g.h),x1=limit(x+w,0,g.w),y1=limit(y+h,0,g.h);
 for(int j=y0;j<y1;j++)for(int i=x0;i<x1;i++)pixel(i,j,color);
}
static void text(int x,int y,const char *s,uint32_t color,int zoom){
 if(zoom<1)zoom=1;
 for(;*s && x<g.w-8*zoom;s++,x+=8*zoom){
  unsigned c=(unsigned char)*s;if(c>=128)c='?';
  for(int row=0;row<8;row++){
   unsigned bits=(uint8_t)font8x8_basic[c][row];
   for(int col=0;col<8;col++)if(bits&(1u<<col))
    rect(x+col*zoom,y+row*zoom,zoom,zoom,color);
  }
 }
}
static void cursor(void){
 rect(mx-8,my,17,2,0x101010);
 rect(mx,my-8,2,17,0x101010);
 rect(mx-6,my,13,2,ACCENT);
 rect(mx,my-6,2,13,ACCENT);
}
static int fb_init(void){
 g.fd=open("/dev/fb0",O_RDWR);if(g.fd<0)return -1;
 if(ioctl(g.fd,FBIOGET_VSCREENINFO,&g.var)||ioctl(g.fd,FBIOGET_FSCREENINFO,&g.fix))return -1;
 g.w=(int)g.var.xres;g.h=(int)g.var.yres;g.bpp=(int)g.var.bits_per_pixel/8;
 if(g.w<320||g.h<200||g.w>4096||g.h>2160||(g.bpp!=2&&g.bpp!=3&&g.bpp!=4))return -1;
 g.memsize=g.fix.smem_len;
 if(g.memsize<g.fix.line_length*(size_t)g.h)return -1;
 g.mem=mmap(NULL,g.memsize,PROT_READ|PROT_WRITE,MAP_SHARED,g.fd,0);
 if(g.mem==MAP_FAILED){g.mem=NULL;return -1;}
 mx=g.w/2;my=g.h/2;return 0;
}
static int suffix(const char *n,const char *ext){
 size_t a=strlen(n),b=strlen(ext);
 return a>=b && !strcasecmp(n+a-b,ext);
}
static int media_supported(const char *s,int kind){
 if(!kind)return suffix(s,".jpg")||suffix(s,".jpeg")||suffix(s,".png")||suffix(s,".bmp")||suffix(s,".ppm");
 return suffix(s,".x360v");
}
static void scan_dir(const char *path,int kind){
 DIR *dir=opendir(path);if(!dir)return;
 struct dirent *e;
 while((e=readdir(dir))!=NULL&&nfiles<MAX_MEDIA){
  if(e->d_name[0]=='.'||!media_supported(e->d_name,kind))continue;
  Media *f=&list[nfiles];
  int len=snprintf(f->file,sizeof(f->file),"%s/%s",path,e->d_name);
  if(len<0||(size_t)len>=sizeof(f->file))continue;
  struct stat st;
  if(stat(f->file,&st)||!S_ISREG(st.st_mode))continue;
  snprintf(f->label,sizeof(f->label),"%s",e->d_name);
  nfiles++;
 }
 closedir(dir);
}
static void refresh(int kind){
 nfiles=0;selected=0;
 scan_dir(kind?"/media/usb/X360MEDIA/VIDEOS":"/media/usb/X360MEDIA/PHOTOS",kind);
 scan_dir(kind?"/usr/share/x360linux/videos":"/usr/share/x360linux/photos",kind);
}
static int u16(const uint8_t *b){return b[0]|b[1]<<8;}
static uint32_t u32(const uint8_t *b){return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;}
static int video_info(FILE *f,int *w,int *h,int *fps,uint32_t *frames){
 uint8_t head[16];
 if(fread(head,1,16,f)!=16||memcmp(head,"X36V",4))return -1;
 *w=u16(head+4);*h=u16(head+6);*fps=(int)u32(head+8);*frames=u32(head+12);
 if(*w<16||*h<16||*w>640||*h>360||*fps<1||*fps>30||*frames==0||*frames>900)return -1;
 return 0;
}
static int self_test(int argc,char **argv){
 if(argc!=4){fprintf(stderr,"usage: x360desk --self-test sample.png sample.x360v\n");return 2;}
 int w,h,chan;
 if(!stbi_info(argv[2],&w,&h,&chan)||w<=0||h<=0||((uint64_t)w*h)>LIMIT_PIXELS){
  fprintf(stderr,"image decode probe failed\n");return 1;
 }
 FILE *f=fopen(argv[3],"rb");if(!f)return 1;
 int fps;uint32_t frames;
 int ok=video_info(f,&w,&h,&fps,&frames)==0;
 if(ok){
  if(fseek(f,0,SEEK_END))ok=0;
  else{
   long size=ftell(f);
   uint64_t required=16+(uint64_t)w*h*3*frames;
   if(size<0||(uint64_t)size!=required)ok=0;
  }
 }
 fclose(f);
 if(!ok){fprintf(stderr,"X36V validation failed\n");return 1;}
 printf("X360DESK_MEDIA_SELFTEST_OK (image + X36V)\n");
 return 0;
}
static int hasbit(int fd,unsigned which,unsigned bit){
 unsigned long bits[(KEY_MAX+8*sizeof(long))/(8*sizeof(long))]={0};
 size_t n=sizeof(bits);
 if(ioctl(fd,EVIOCGBIT(which,n),bits)<0)return 0;
 if(bit>=n*8)return 0;
 return !!(bits[bit/(8*sizeof(long))]&(1ul<<(bit%(8*sizeof(long)))));
}
static void input_open(void){
 for(int i=0;i<24;i++){
  char name[64];snprintf(name,sizeof(name),"/dev/input/event%d",i);
  int fd=open(name,O_RDONLY|O_NONBLOCK);if(fd<0)continue;
  if(gamepad_fd<0&&hasbit(fd,EV_KEY,BTN_SOUTH)&&hasbit(fd,EV_ABS,ABS_X))gamepad_fd=fd;
  else if(keyboard_fd<0&&hasbit(fd,EV_KEY,KEY_ENTER)&&hasbit(fd,EV_KEY,KEY_Q))keyboard_fd=fd;
  else close(fd);
 }
}
static int key_down(int fd,int code){
 return (fd>=0&&code>=0&&code<=KEY_MAX&&buttons[code])?1:0;
}
static int action=0;
static void pump_input(void){
 int fds[]={gamepad_fd,keyboard_fd};
 struct input_event ev;
 for(int i=0;i<2;i++)if(fds[i]>=0){
  while(read(fds[i],&ev,sizeof(ev))==sizeof(ev)){
   if(ev.type==EV_ABS){
    if(ev.code==ABS_X)ax=ev.value;
    else if(ev.code==ABS_Y)ay=ev.value;
    else if(ev.code==ABS_HAT0X){dx=ev.value;if(dx)selected+=dx;}
    else if(ev.code==ABS_HAT0Y){dy=ev.value;if(dy)selected+=dy;}
   }else if(ev.type==EV_KEY){
    if(ev.code<KEY_MAX)buttons[ev.code]=(uint8_t)!!ev.value;
    if(ev.value==1){
     if(ev.code==BTN_SOUTH||ev.code==KEY_ENTER)action=1;
     if(ev.code==BTN_EAST||ev.code==KEY_ESC)action=2;
     if(ev.code==KEY_Q)action=3;
     if(ev.code==KEY_DOWN||ev.code==BTN_DPAD_DOWN)selected++;
     if(ev.code==KEY_UP||ev.code==BTN_DPAD_UP)selected--;
    }
   }
  }
 }
 if(abs(ax)>6000||abs(ay)>6000){
  mx=limit(mx+ax/6500,4,g.w-4);
  my=limit(my+ay/6500,4,g.h-4);
 }
}
static void draw_rgb(const uint8_t *img,int iw,int ih,int top,int bottom){
 if(iw<1||ih<1)return;
 int maxw=g.w-30,maxh=bottom-top-12;
 if(maxw<1||maxh<1)return;
 int dw=maxw,dh=(int)((int64_t)ih*dw/iw);
 if(dh>maxh){dh=maxh;dw=(int)((int64_t)iw*dh/ih);}
 if(dw<1||dh<1)return;
 int x=(g.w-dw)/2,y=top+(maxh-dh)/2;
 for(int py=0;py<dh;py++){
  int sy=(int)((int64_t)py*ih/dh);
  for(int px=0;px<dw;px++){
   int sx=(int)((int64_t)px*iw/dw);
   const uint8_t *q=img+3*((size_t)sy*iw+sx);
   pixel(x+px,y+py,(uint32_t)q[0]<<16|(uint32_t)q[1]<<8|q[2]);
  }
 }
}
static void title(const char *section){
 rect(0,0,g.w,g.h,SCREEN_BG);
 rect(0,0,g.w,5,ACCENT);
 text(18,22,"X360LINUX",TEXT,2);
 text(18,58,section,MUTED,1);
 rect(0,g.h-39,g.w,39,0x182430);
 text(18,g.h-26,"STICK: CURSOR  A: OPEN  B: BACK  USB MEDIA: READ-ONLY",MUTED,1);
}
static void photo_show(const char *filename){
 int w=0,h=0,c=0;
 if(!stbi_info(filename,&w,&h,&c)||w<1||h<1||(uint64_t)w*h>LIMIT_PIXELS)return;
 unsigned char *rgb=stbi_load(filename,&w,&h,&c,3);if(!rgb)return;
 title("PHOTO VIEWER | B TO RETURN");
 draw_rgb(rgb,w,h,90,g.h-60);cursor();
 stbi_image_free(rgb);
 action=0;
 for(;;){pump_input();if(action==2||action==3||action==1)break;usleep(35000);}
 action=0;
}
static void video_show(const char *filename){
 FILE *f=fopen(filename,"rb");if(!f)return;
 int w,h,fps;uint32_t frames;
 if(video_info(f,&w,&h,&fps,&frames)){fclose(f);return;}
 size_t bytes=(size_t)w*h*3;
 uint8_t *buf=malloc(bytes);if(!buf){fclose(f);return;}
 action=0;int paused=0;
 for(uint32_t i=0;i<frames;){
  pump_input();
  if(action==2||action==3)break;
  if(action==1){paused=!paused;action=0;}
  if(paused){usleep(30000);continue;}
  if(fread(buf,1,bytes,f)!=bytes)break;
  title("VIDEO PLAYER | A PAUSE  B BACK | NO AUDIO");
  draw_rgb(buf,w,h,90,g.h-65);
  char label[80];snprintf(label,sizeof(label),"FRAME %u / %u  %u FPS",(unsigned)(i+1),(unsigned)frames,(unsigned)fps);
  text(20,g.h-52,label,TEXT,1);cursor();
  ++i;
  usleep(1000000u/(unsigned)fps);
 }
 free(buf);fclose(f);action=0;
}
static void draw_home(void){
 title("LIGHTWEIGHT POWERPC DESKTOP | v0.3 PREVIEW");
 int ww=(g.w-68)/3;
 const char *labels[]={"PHOTOS","VIDEOS","SYSTEM"};
 const char *descs[]={"JPG PNG BMP","X36V SILENT","DEVICE STATUS"};
 for(int i=0;i<3;i++){
  int x=20+i*(ww+14),y=g.h/3,h=g.h/3;
  rect(x,y,ww,h,selected==i?0x235d46:0x21303d);
  rect(x,y,ww,4,selected==i?ACCENT:0x415564);
  text(x+12,y+25,labels[i],TEXT,2);
  text(x+12,y+70,descs[i],MUTED,1);
 }
 text(20,g.h-68,"DEBIAN PORTS: PLANNED | NO GPU ACCELERATION",MUTED,1);
 cursor();
}
static void draw_list(void){
 title(tab==0?"PHOTOS | USB + DEMO":"VIDEOS | USB + DEMO  (X36V ONLY)");
 char s[120];snprintf(s,sizeof(s),"%d FILE(S) FOUND",nfiles);
 text(20,88,s,MUTED,1);
 int nvisible=limit((g.h-165)/31,2,18),start=selected>=nvisible?selected-nvisible+1:0;
 for(int j=0;j<nvisible&&start+j<nfiles;j++){
  int idx=start+j,y=117+j*31;
  rect(20,y,g.w-40,28,idx==selected?0x235d46:0x1a2533);
  text(29,y+7,list[idx].label,TEXT,1);
 }
 if(!nfiles)text(20,138,"NO FILES. PLACE FILES IN X360MEDIA ON USB.",TEXT,1);
 cursor();
}
static void draw_system(void){
 title("SYSTEM INFORMATION");
 text(22,110,"X360LINUX 0.3: GRAPHICAL PREVIEW",TEXT,2);
 text(22,168,"KERNEL: XENON LINUX | USERSPACE: PPC32",TEXT,1);
 text(22,200,"STORAGE: USB FAT32 READ-ONLY",TEXT,1);
 text(22,233,"CONTROLLER: /DEV/INPUT/EVDEV",TEXT,1);
 text(22,268,"IMAGES: JPG, PNG, BMP, PPM",TEXT,1);
 text(22,302,"VIDEO: X36V (SILENT / CONVERT ON PC)",TEXT,1);
 text(22,336,"DEBIAN DESKTOP + MP4: NOT INCLUDED",MUTED,1);
 cursor();
}
int main(int argc,char **argv){
 if(argc>1&&strcmp(argv[1],"--self-test")==0)return self_test(argc,argv);
 if(fb_init()!=0){
  fprintf(stderr,"X360DESK: /dev/fb0 framebuffer unavailable; using BusyBox shell.\n");
  return 3;
 }
 input_open();mode=0;selected=0;tab=0;
 while(!should_exit){
  pump_input();
  if(mode==0){
   selected=limit(selected,0,2);
   if(action==1){
    int ww=(g.w-68)/3;
    if(my>=g.h/3&&my<2*g.h/3){
     int maybe=(mx-20)/(ww+14);
     if(maybe>=0&&maybe<=2)selected=maybe;
    }
    if(selected==2)mode=3;
    else {tab=selected;mode=1;refresh(tab);}
   }else if(action==3)should_exit=1;
   draw_home();
  }else if(mode==1){
   selected=limit(selected,0,nfiles>0?nfiles-1:0);
   if(action==2)mode=0;
   else if(action==1&&nfiles>0){
    char path[512];memcpy(path,list[selected].file,sizeof(path));
    if(tab==0)photo_show(path);else video_show(path);
   }
   if(mode==1)draw_list();
  }else{
   if(action==2)mode=0;
   if(mode==3)draw_system();
  }
  if(action==3)should_exit=1;
  action=0;
  usleep(70000);
 }
 if(g.mem)munmap(g.mem,g.memsize);
 if(g.fd>=0)close(g.fd);
 if(gamepad_fd>=0)close(gamepad_fd);
 if(keyboard_fd>=0)close(keyboard_fd);
 puts("X360DESK: exiting to terminal.");
 return 0;
}
