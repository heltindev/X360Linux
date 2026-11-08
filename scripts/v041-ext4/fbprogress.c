/* X360Linux v0.4.1-dev early Linux framebuffer progress.
 * PowerPC32 big-endian, no libc; old Linux 2.6 syscall ABI.
 * NOT run in XeLL or before the kernel framebuffer is available.
 * Shows measured boot MILESTONES, NOT a fake timer or a measured throughput percent.
 */
#include <linux/fb.h>
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

static long call3(long n,long a,long b,long c) {
 register long r0 __asm__("r0")=n;
 register long r3 __asm__("r3")=a;
 register long r4 __asm__("r4")=b;
 register long r5 __asm__("r5")=c;
 __asm__ __volatile__("sc" : "+r"(r3) : "r"(r0),"r"(r4),"r"(r5) : "memory","cr0","r6","r7","r8","r9","r10","r11","r12");
 return r3;
}
static long call1(long n,long a){return call3(n,a,0,0);}
static long open_fb(void){return call3(5,(long)"/dev/fb0",2,0);}
static long seek_fb(long f,long offset){return call3(19,f,offset,0);}
static long write_fb(long f,const void* b,long l){return call3(4,f,(long)b,l);}

static u8 line[8192];
static unsigned long fbfd, stride;
static unsigned int width,height,bpp, redoff,greenoff,blueoff,redlen,greenlen,bluelen;
static u32 pixel(u8 r,u8 g,u8 b) {
 return ((u32)(r >> (8-redlen)) << redoff)|
        ((u32)(g >> (8-greenlen)) << greenoff)|
        ((u32)(b >> (8-bluelen)) << blueoff);
}
static void rect(int x,int y,int w,int h,u8 r,u8 g,u8 b) {
 int bytes=bpp/8;
 if(x<0){w+=x;x=0;}
 if(y<0){h+=y;y=0;}
 if(w<=0||h<=0||x>=(int)width||y>=(int)height)return;
 if(x+w>(int)width)w=(int)width-x;
 if(y+h>(int)height)h=(int)height-y;
 if(w*bytes>(int)sizeof(line))w=sizeof(line)/bytes;
 u32 color=pixel(r,g,b);
 for(int i=0;i<w;i++){
  for(int j=0;j<bytes;j++) {
   line[i*bytes+j]=(u8)(color>>(8*(bytes-1-j)));
  }
 }
 for(int row=0;row<h;row++){
  if(seek_fb(fbfd,(y+row)*stride+x*bytes)<0)return;
  if(write_fb(fbfd,line,w*bytes)<0)return;
 }
}
static const u8 font[11][7]={
 {14,17,19,21,25,17,14},  /*0*/
 {4,12,4,4,4,4,14},        /*1*/
 {14,17,1,2,4,8,31},      /*2*/
 {30,1,1,14,1,1,30},      /*3*/
 {2,6,10,18,31,2,2},      /*4*/
 {31,16,16,30,1,1,30},    /*5*/
 {14,16,16,30,17,17,14},  /*6*/
 {31,1,2,4,8,8,8},        /*7*/
 {14,17,17,14,17,17,14},  /*8*/
 {14,17,17,15,1,1,14},    /*9*/
 {17,18,4,8,17,0,0}      /*%*/
};
static void glyph(int x,int y,int ch,int scale){
 if(ch<0||ch>10)return;
 for(int i=0;i<7;i++)
  for(int j=0;j<5;j++)
   if(font[ch][i]&(1<<(4-j)))rect(x+j*scale,y+i*scale,scale,scale,194,242,206);
}
int main(int argc,char**argv){
 int pct=0;
 if(argc>1) {
  const char*s=argv[1];int val=0;
  while(*s>='0'&&*s<='9'){val=val*10+*s-'0';s++;}
  pct=val>100?100:val;
 }
 long fd=open_fb();
 if(fd<0)return 0;  /* No framebuffer: normal boot proceeds, logs preserved. */
 struct fb_fix_screeninfo fix;
 struct fb_var_screeninfo var;
 if(call3(54,fd,0x4602,(long)&fix)<0 || call3(54,fd,0x4600,(long)&var)<0){
  call1(6,fd);return 0;
 }
 if(var.xres<320||var.yres<200||var.xres>4096||var.yres>2160||
    (var.bits_per_pixel!=16 && var.bits_per_pixel!=24 && var.bits_per_pixel!=32)||
    !var.red.length||!var.green.length||!var.blue.length) {call1(6,fd);return 0;}
 fbfd=(unsigned long)fd;stride=fix.line_length;
 width=var.xres;height=var.yres;bpp=var.bits_per_pixel;
 redoff=var.red.offset;greenoff=var.green.offset;blueoff=var.blue.offset;
 redlen=var.red.length;greenlen=var.green.length;bluelen=var.blue.length;
 if(redlen>8||greenlen>8||bluelen>8){call1(6,fd);return 0;}
 int w=(int)width*55/100; if(w>610)w=610;
 int x=(width-w)/2, y=height*58/100;
 rect(x-15,y-75,w+30,150,11,24,16);
 rect(x-4,y-4,w+8,26,62,87,67);
 rect(x,y,w,18,20,42,28);
 if(pct>0)rect(x,y,w*pct/100,18,56,221,96);
 int nums[3],len=0;int v=pct;
 do {nums[len++]=v%10;v/=10;}while(v&&len<3);
 int scale=3, glyphw=18;
 int total=(len+1)*glyphw;
 int cx=x+(w-total)/2;
 for(int i=len-1;i>=0;i--){glyph(cx,y+40,nums[i],scale);cx+=glyphw;}
 glyph(cx,y+40,10,scale);
 call1(6,fd);
 return 0;
}
__asm__(".text\n.globl _start\n_start:\n"
 "lwz 3,0(1)\n"
 "addi 4,1,4\n"
 "bl main\n"
 "li 0,1\n"
 "sc\n"
 "b .\n");
