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
#include <time.h>
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
static int font_scale=2, pad=24, gap=16, foot_h=46, header_h=90;
static int stick_center_x=0,stick_center_y=0,stick_range_x=32767,stick_range_y=32767;
static int left_pressed=0, right_pressed=0;
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
/* Filled bars are the core of the UI. Avoid per-pixel function calls for
 * every background rectangle on a software framebuffer (512 MB system).
 * The framebuffer pitch, offsets and color bitfields remain hardware-defined. */
static void rect(int x,int y,int w,int h,uint32_t color){
 int x0=limit(x,0,g.w),y0=limit(y,0,g.h);
 int x1=limit(x+w,0,g.w),y1=limit(y+h,0,g.h);
 if(x1<=x0||y1<=y0)return;
 uint32_t packed=scalechan((color>>16)&255,g.var.red)|
   scalechan((color>>8)&255,g.var.green)|scalechan(color&255,g.var.blue);
 for(int j=y0;j<y1;j++){
  size_t row=(size_t)(j+g.var.yoffset)*g.fix.line_length+
   (size_t)(x0+g.var.xoffset)*(unsigned)g.bpp;
  if(row+(size_t)(x1-x0)*(unsigned)g.bpp>g.memsize)break;
  uint8_t *out=g.mem+row;
  if(g.bpp==4){
   for(int i=x0;i<x1;i++,out+=4)memcpy(out,&packed,4);
  }else if(g.bpp==2){
   uint16_t packed16=(uint16_t)packed;
   for(int i=x0;i<x1;i++,out+=2)memcpy(out,&packed16,2);
  }else{
   for(int i=x0;i<x1;i++,out+=3){
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    out[0]=(packed>>16)&255;out[1]=(packed>>8)&255;out[2]=packed&255;
#else
    out[0]=packed&255;out[1]=(packed>>8)&255;out[2]=(packed>>16)&255;
#endif
   }
  }
 }
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
 int radius=font_scale*5;
 /* High contrast pointer: clear even on a TV viewed from a distance. */
 rect(mx-radius,my,2*radius+1,3,0x04140a);
 rect(mx,my-radius,3,2*radius+1,0x04140a);
 rect(mx-radius+2,my,2*radius-3,2,ACCENT);
 rect(mx,my-radius+2,2,2*radius-3,ACCENT);
}
static void sizing(void){
 /* Match the dashboard's inherited 720p/1080p framebuffer.
  * Keep headings, menu options and help text legible at TV distance. */
 font_scale=limit(g.h/255,2,5); /* 720p -> 2, 1080p -> 4 */
 pad=limit(g.w/22,24,90);
 gap=limit(g.w/85,12,32);
 header_h=limit(g.h/6,104,190);
 foot_h=limit(g.h/9,58,126);
}
static int card_width(void){return (g.w-2*pad-2*gap)/3;}
static int card_height(void){return limit(g.h/3,200,390);}
static int card_top(void){return (g.h-card_height())/2+30;}
static int hover_card(void){
 int ww=card_width(),yy=card_top();
 if(my<yy||my>yy+card_height())return -1;
 for(int i=0;i<3;i++){
  int x=pad+i*(ww+gap);
  if(mx>=x && mx<=x+ww)return i;
 }
 return -1;
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
 mx=g.w/2;my=g.h/2;sizing();return 0;
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
 for(int i=0;i<32;i++){
  char name[64];snprintf(name,sizeof(name),"/dev/input/event%d",i);
  int fd=open(name,O_RDONLY|O_NONBLOCK);if(fd<0)continue;
  if(gamepad_fd<0&&hasbit(fd,EV_KEY,BTN_SOUTH)&&hasbit(fd,EV_ABS,ABS_X)){
   gamepad_fd=fd;
   struct input_absinfo center;
   if(ioctl(fd,EVIOCGABS(ABS_X),&center)==0){
    stick_center_x=(center.minimum+center.maximum)/2;
    stick_range_x=(center.maximum-center.minimum)/2;
    if(stick_range_x<1)stick_range_x=1;
   }
   if(ioctl(fd,EVIOCGABS(ABS_Y),&center)==0){
    stick_center_y=(center.minimum+center.maximum)/2;
    stick_range_y=(center.maximum-center.minimum)/2;
    if(stick_range_y<1)stick_range_y=1;
   }
  }else if(keyboard_fd<0&&hasbit(fd,EV_KEY,KEY_ENTER)&&hasbit(fd,EV_KEY,KEY_Q))keyboard_fd=fd;
  else close(fd);
 }
}
static int action=0;
static int usb_available(void){
 struct stat st;
 return stat("/media/usb/X360MEDIA",&st)==0 && S_ISDIR(st.st_mode);
}
static int moving_pointer=0;
static void pump_input(void){
 int fds[]={gamepad_fd,keyboard_fd};
 struct input_event ev;
 moving_pointer=0;
 for(int i=0;i<2;i++)if(fds[i]>=0){
  while(read(fds[i],&ev,sizeof(ev))==sizeof(ev)){
   if(ev.type==EV_ABS){
    if(ev.code==ABS_X)ax=ev.value;
    else if(ev.code==ABS_Y)ay=ev.value;
    else if(ev.code==ABS_HAT0X){
     if(ev.value && !dx && mode==0)selected=limit(selected+ev.value,0,2);
     dx=ev.value;
    }else if(ev.code==ABS_HAT0Y){
     if(ev.value && !dy && mode==1)selected+=ev.value;
     dy=ev.value;
    }
   }else if(ev.type==EV_KEY){
    if(ev.code<KEY_MAX)buttons[ev.code]=(uint8_t)!!ev.value;
    if(ev.value==1){
     if(ev.code==BTN_SOUTH||ev.code==KEY_ENTER)action=1;
     if(ev.code==BTN_EAST||ev.code==KEY_ESC)action=2;
     if(ev.code==KEY_Q)action=3;
     if(ev.code==KEY_DOWN||ev.code==BTN_DPAD_DOWN)selected++;
     if(ev.code==KEY_UP||ev.code==BTN_DPAD_UP)selected--;
     if(ev.code==KEY_LEFT && mode==0)selected--;
     if(ev.code==KEY_RIGHT && mode==0)selected++;
    }
   }
  }
 }
 int speed=limit(g.w/200,4,12);
 int vx=(ax-stick_center_x)*speed/stick_range_x;
 int vy=(ay-stick_center_y)*speed/stick_range_y;
 if(vx>=2||vx<=-2||vy>=2||vy<=-2){
  mx=limit(mx+vx,pad/2,g.w-pad/2);
  my=limit(my+vy,pad/2,g.h-pad/2);
  moving_pointer=1;
 }
 if(mode==0&&moving_pointer){
  int hover=hover_card();
  if(hover>=0)selected=hover;
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
 rect(0,0,g.w,7,ACCENT);
 /* Header title and status are scalable, with a 4-5% safe area. */
 text(pad,header_h/5,"X360LINUX",TEXT,font_scale+1);
 text(pad,header_h/5+(font_scale+1)*11,section,MUTED,font_scale);
 rect(pad,header_h-8,g.w-2*pad,2,0x365d54);
 rect(0,g.h-foot_h,g.w,foot_h,0x182430);
 text(pad,g.h-foot_h+(foot_h-8*font_scale)/2,
      "LEFT STICK : MOVE    A : OPEN    B : BACK",TEXT,font_scale);
}
static void photo_show(const char *filename){
 int w=0,h=0,c=0;
 if(!stbi_info(filename,&w,&h,&c)||w<1||h<1||(uint64_t)w*h>LIMIT_PIXELS)return;
 unsigned char *rgb=stbi_load(filename,&w,&h,&c,3);if(!rgb)return;
 title("PHOTO VIEWER | B TO RETURN");
 draw_rgb(rgb,w,h,header_h+8,g.h-foot_h-12);cursor();
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
  draw_rgb(buf,w,h,header_h+8,g.h-foot_h-20);
  char label[80];snprintf(label,sizeof(label),"FRAME %u / %u  %u FPS",(unsigned)(i+1),(unsigned)frames,(unsigned)fps);
  text(pad,g.h-foot_h-13-font_scale*8,label,TEXT,font_scale);cursor();
  ++i;
  usleep(1000000u/(unsigned)fps);
 }
 free(buf);fclose(f);action=0;
}
static void draw_home(void){
 title("DESKTOP PREVIEW  |  POWERPC XENON");
 int ww=card_width(),top=card_top(),hh=card_height();
 const char *labels[]={"PHOTOS","VIDEOS","SYSTEM"};
 const char *descs[]={"JPG  PNG  BMP","SILENT X36V","LINUX STATUS"};
 const char *icons[]={"[ P ]","[ > ]","[ i ]"};
 for(int i=0;i<3;i++){
  int x=pad+i*(ww+gap);
  uint32_t bg=selected==i?0x1b5946:0x263746;
  rect(x,top,ww,hh,bg);
  rect(x,top,ww,selected==i?9:4,selected==i?ACCENT:0x54766d);
  if(selected==i){
   rect(x,top+hh-7,ww,7,ACCENT);
  }
  text(x+gap,top+hh/6,icons[i],selected==i?ACCENT:TEXT,font_scale+1);
  text(x+gap,top+hh/2-8*font_scale,labels[i],TEXT,font_scale+1);
  text(x+gap,top+hh/2+13*font_scale,descs[i],MUTED,font_scale);
 }
 cursor();
}
static void draw_list(void){
 title(tab==0?"PHOTOS - USB + INCLUDED DEMO":"VIDEOS - SILENT X36V + INCLUDED DEMO");
 char s[120];snprintf(s,sizeof(s),"%d FILE(S) FOUND",nfiles);
 text(pad,header_h+font_scale*5,s,MUTED,font_scale);
 int line_h=font_scale*15;
 int nvisible=limit((g.h-header_h-foot_h-80)/line_h,2,18);
 int start=selected>=nvisible?selected-nvisible+1:0;
 for(int j=0;j<nvisible&&start+j<nfiles;j++){
  int idx=start+j,y=header_h+font_scale*15+j*line_h;
  rect(pad,y,g.w-2*pad,line_h-5,idx==selected?0x235d46:0x1d2b39);
  text(pad+gap,y+font_scale*3,list[idx].label,TEXT,font_scale);
 }
 if(!nfiles)text(pad,header_h+font_scale*19,
   "NO FILES FOUND. COPY MEDIA TO USB.",TEXT,font_scale);
 cursor();
}
static void draw_system(void){
 title("SYSTEM STATUS");
 int lh=font_scale*19,y=header_h+font_scale*10;
 text(pad,y,"X360LINUX - GRAPHICAL TEST",TEXT,font_scale+1);y+=lh+12;
 const char *lines[]={
  "LINUX: XENON KERNEL + PPC32 USERSPACE",
  "DISPLAY: FRAMEBUFFER (NO GPU ACCEL)",
  "MEDIA: JPG PNG BMP + SILENT X36V",
  "MEDIA: JPG PNG BMP + SILENT X36V",
  "DEBIAN PORTS: EXPERIMENTAL BASE"
 };
 for(unsigned i=0;i<sizeof(lines)/sizeof(lines[0]);i++,y+=lh)
  text(pad,y,lines[i],i==4?MUTED:TEXT,font_scale);
 y+=lh;
 text(pad,y,gamepad_fd>=0?"GAMEPAD: DETECTED":"GAMEPAD: NOT DETECTED",gamepad_fd>=0?ACCENT:0xdba35f,font_scale);y+=lh;
 text(pad,y,keyboard_fd>=0?"KEYBOARD: DETECTED":"KEYBOARD: NOT DETECTED",keyboard_fd>=0?ACCENT:MUTED,font_scale);y+=lh;
 text(pad,y,usb_available()?"USB MEDIA: MOUNTED READ-ONLY":"USB MEDIA: NOT MOUNTED",usb_available()?ACCENT:MUTED,font_scale);
 cursor();
}
/* Headless framebuffer screenshot test on the PPC32 emulator.
 * Writes a genuine PPM file; no /dev/fb0 or Xbox 360 console needed. */
static int render_test(int argc,char **argv){
 if(argc!=5){fprintf(stderr,"usage: x360desk --render-test WIDTH HEIGHT out.ppm\n");return 2;}
 int w=atoi(argv[2]),h=atoi(argv[3]);
 if(w<640||h<360||w>1920||h>1080)return 2;
 g.w=w;g.h=h;g.fd=-1;g.bpp=4;
 g.fix.line_length=(unsigned)w*4;
 g.memsize=(size_t)w*h*4;
 g.var.bits_per_pixel=32;
 g.var.red.offset=16;g.var.red.length=8;
 g.var.green.offset=8;g.var.green.length=8;
 g.var.blue.offset=0;g.var.blue.length=8;
 g.mem=calloc(1,g.memsize);if(!g.mem)return 3;
 sizing();mx=w/2;my=h/2;selected=0;
 draw_home();
 FILE *out=fopen(argv[4],"wb");
 if(!out){free(g.mem);return 4;}
 fprintf(out,"P6\n%d %d\n255\n",w,h);
 for(int y=0;y<h;y++)for(int x=0;x<w;x++){
  uint32_t v;
  memcpy(&v,g.mem+((size_t)y*w+x)*4,4);
  unsigned char rgb[3]={(unsigned char)(v>>16),
                       (unsigned char)(v>>8),
                       (unsigned char)v};
  fwrite(rgb,1,3,out);
 }
 int fail=fclose(out);
 free(g.mem);g.mem=NULL;
 if(fail)return 5;
 printf("X360DESK_LAYOUT_RENDER_OK %d %d scale=%d\n",w,h,font_scale);
 return 0;
}

int main(int argc,char **argv){
 if(argc>1&&strcmp(argv[1],"--render-test")==0)return render_test(argc,argv);
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
     /* Controller D-pad chooses cards; moving the stick also focuses
      * the hovered card. No stray focus jumps on initial startup. */
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
  usleep(85000);
 }
 if(g.mem)munmap(g.mem,g.memsize);
 if(g.fd>=0)close(g.fd);
 if(gamepad_fd>=0)close(gamepad_fd);
 if(keyboard_fd>=0)close(keyboard_fd);
 puts("X360DESK: exiting to terminal.");
 return 0;
}
