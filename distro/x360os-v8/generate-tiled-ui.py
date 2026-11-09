#!/usr/bin/env python3
"""Build a new, standalone Xbox 360 framebuffer UI from the project source.

The prior v7 alpha corrupted video because it treated the Xenos tiled 32bpp
surface as a linear framebuffer. Free60 XeLL xenos.c has the exact tile
address formula used here; no Xorg, GNOME or Ubuntu dependencies are introduced.
"""
from pathlib import Path

here = Path(__file__).resolve().parent
src = here.parent / "x360os-native" / "x360os-ui.c"
s = src.read_text(encoding="utf-8")
assert "static void pixel(int x,int y,uint32_t color)" in s
assert "static void text(int x,int y,const char *s" in s
assert "static int fb_init(void)" in s
assert "static int render_test(int argc,char **argv)" in s

s = s.replace("int w,h,bpp;\n} Display;", "int w,h,bpp;int tiled;unsigned tiled_pitch;\n} Display;")
s = s.replace(
    "static void pixel(int x,int y,uint32_t color){",
    "static void pixel(int x,int y,uint32_t color){", 1
)
start = s.index("static void pixel(int x,int y,uint32_t color){")
end = s.index("static void text(int x,int y,const char *s", start)
replace = r"""
/* Pixel address from Free60 XeLL xenos.c, xenos_pset32().
 * Xenos 32x32 tiled framebuffer is NOT row-major. Xorg xenosfb hides
 * this for legacy Linux; this native driver works without Xorg.
 *
 * xenos_width is the framebuffer stride in pixels, rounded up to 32.
 * The output is a pixel/word index, not a byte offset.
 */
static size_t xenos_pixel_offset(unsigned x,unsigned y,unsigned pitch) {
 size_t macro = (size_t)(y >> 5) * 32u * pitch + ((size_t)(x >> 5) << 10);
 size_t micro = (x & 3u) + ((y & 1u) << 2)
               + (((x & 31u) >> 2) << 3)
               + (((y & 31u) >> 1) << 6);
 return (macro + micro) ^ ((size_t)(y & 8u) << 2);
}
/* Free60 XeLL stores BGRA-like GPU words: B:G:R:00 in big-endian RAM. */
static uint32_t xenos_word(uint32_t color) {
 return ((color & 255u) << 24) |
        (((color >> 8) & 255u) << 16) |
        (((color >> 16) & 255u) << 8);
}
static uint32_t normal_word(uint32_t color) {
 return scalechan((color >> 16) & 255,g.var.red) |
        scalechan((color >> 8) & 255,g.var.green) |
        scalechan(color & 255,g.var.blue);
}
static size_t pixel_address(int x,int y) {
 unsigned xx=(unsigned)(x+g.var.xoffset),yy=(unsigned)(y+g.var.yoffset);
 if(g.tiled) return xenos_pixel_offset(xx,yy,g.tiled_pitch)*4u;
 return (size_t)yy*g.fix.line_length+(size_t)xx*(unsigned)g.bpp;
}
static void pixel(int x,int y,uint32_t color) {
 if(x<0||y<0||x>=g.w||y>=g.h)return;
 size_t off=pixel_address(x,y);
 if(off+(size_t)g.bpp>g.memsize)return;
 uint32_t v=g.tiled?xenos_word(color):normal_word(color);
 if(g.bpp==4)memcpy(g.mem+off,&v,4);
 else if(g.bpp==2){uint16_t q=(uint16_t)v;memcpy(g.mem+off,&q,2);}
 else if(g.bpp==3){
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
  g.mem[off]=(v>>16)&255;g.mem[off+1]=(v>>8)&255;g.mem[off+2]=v&255;
#else
  g.mem[off]=v&255;g.mem[off+1]=(v>>8)&255;g.mem[off+2]=(v>>16)&255;
#endif
 }
}
static void rect(int x,int y,int w,int h,uint32_t color){
 int x0=limit(x,0,g.w),y0=limit(y,0,g.h);
 int x1=limit(x+w,0,g.w),y1=limit(y+h,0,g.h);
 if(x1<=x0||y1<=y0)return;
 uint32_t v=g.tiled?xenos_word(color):normal_word(color);
 for(int py=y0;py<y1;py++)for(int px=x0;px<x1;px++){
  size_t off=pixel_address(px,py);
  if(off+(size_t)g.bpp>g.memsize)continue;
  if(g.bpp==4)memcpy(g.mem+off,&v,4);
  else if(g.bpp==2){uint16_t q=(uint16_t)v;memcpy(g.mem+off,&q,2);}
  else{
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   g.mem[off]=(v>>16)&255;g.mem[off+1]=(v>>8)&255;g.mem[off+2]=v&255;
#else
   g.mem[off]=v&255;g.mem[off+1]=(v>>8)&255;g.mem[off+2]=(v>>16)&255;
#endif
  }
 }
}
"""
s = s[:start] + replace + s[end:]
fbstart = s.index("static int fb_init(void){")
fbend = s.index("static int suffix(", fbstart)
s = s[:fbstart] + r"""
/* Linux Xenos framebuffer: 32-bit 32x32 tiled, even when fbdev reports a
 * conventional line_length. Keep the display's original mode unchanged.
 */
static int fb_init(void) {
 g.fd=open("/dev/fb0",O_RDWR);if(g.fd<0)return -1;
 if(ioctl(g.fd,FBIOGET_VSCREENINFO,&g.var)||ioctl(g.fd,FBIOGET_FSCREENINFO,&g.fix))return -1;
 g.w=(int)g.var.xres;g.h=(int)g.var.yres;g.bpp=(int)g.var.bits_per_pixel/8;
 if(g.w<320||g.h<200||g.w>4096||g.h>2160||g.bpp!=4)return -1;
 g.tiled=1;
 /* XeLL uses the native framebuffer pitch, aligned to 32 pixels. */
 unsigned pitch=g.var.xres_virtual > (unsigned)g.w?g.var.xres_virtual:(unsigned)g.w;
 if(g.fix.line_length/4u > pitch) pitch=g.fix.line_length/4u;
 g.tiled_pitch=(pitch+31u)&~31u;
 g.memsize=g.fix.smem_len;
 if(!g.memsize||g.memsize>256u*1024u*1024u)return -1;
 g.mem=mmap(NULL,g.memsize,PROT_READ|PROT_WRITE,MAP_SHARED,g.fd,0);
 if(g.mem==MAP_FAILED){g.mem=NULL;return -1;}
 fprintf(stderr,"X360OS-V8-FB: %dx%d %d-bpp pitch=%u aligned=%u smem=%lu Xenos32 tiled\n",
   g.w,g.h,g.bpp,(unsigned)g.fix.line_length,g.tiled_pitch,(unsigned long)g.memsize);
 mx=g.w/2;my=g.h/2;sizing();return 0;
}
static int fb_info(void){
 struct fb_fix_screeninfo f;struct fb_var_screeninfo v;
 int fd=open("/dev/fb0",O_RDONLY|O_NONBLOCK);
 if(fd<0){perror("/dev/fb0");return 2;}
 if(ioctl(fd,FBIOGET_FSCREENINFO,&f)||ioctl(fd,FBIOGET_VSCREENINFO,&v)){
  perror("fb ioctl");close(fd);return 2;
 }
 fprintf(stderr,"X360OS FB READ ONLY id=%.*s x=%u y=%u xvirt=%u yvirt=%u pitch_bytes=%u bits=%u mem=%u\n",
   16,f.id,v.xres,v.yres,v.xres_virtual,v.yres_virtual,f.line_length,v.bits_per_pixel,f.smem_len);
 close(fd);return 0;
}
""" + s[fbend:]
s = s.replace(
    'if(argc!=5){fprintf(stderr,"usage: x360desk --render-test WIDTH HEIGHT out.ppm\\n");return 2;}',
    'if(argc!=5){fprintf(stderr,"usage: x360os-ui --render-test[-xenos] WIDTH HEIGHT out.ppm\\n");return 2;}\n int xtile=strcmp(argv[1],"--render-test-xenos")==0;')
assert "int xtile=strcmp" in s
s = s.replace(
    "g.fix.line_length=(unsigned)w*4;\n g.memsize=(size_t)w*h*4;",
    "g.tiled=xtile;\n g.tiled_pitch=((unsigned)w+31u)&~31u;\n g.fix.line_length=(unsigned)w*4;\n g.memsize=xtile?(size_t)g.tiled_pitch*(((unsigned)h+31u)&~31u)*4u:(size_t)w*h*4;")
s = s.replace(
    "memcpy(&v,g.mem+((size_t)y*w+x)*4,4);\n  unsigned char rgb[3]={(unsigned char)(v>>16),\n                       (unsigned char)(v>>8),\n                       (unsigned char)v};",
    "size_t off=xtile?xenos_pixel_offset((unsigned)x,(unsigned)y,g.tiled_pitch)*4u:\n                    ((size_t)y*w+x)*4u;\n  if(off+4>g.memsize){free(g.mem);fclose(out);return 6;}\n  memcpy(&v,g.mem+off,4);\n  unsigned char rgb[3]={\n   (unsigned char)(xtile?(v>>8):(v>>16)),\n   (unsigned char)(xtile?(v>>16):(v>>8)),\n   (unsigned char)(xtile?(v>>24):v)};")
assert "xenos_pixel_offset((unsigned)x" in s
s = s.replace(
    'if(argc>1&&strcmp(argv[1],"--render-test")==0)return render_test(argc,argv);',
    'if(argc>1&&(strcmp(argv[1],"--render-test")==0||strcmp(argv[1],"--render-test-xenos")==0))return render_test(argc,argv);\n if(argc>1&&strcmp(argv[1],"--fb-info")==0)return fb_info();'
)
assert '--render-test-xenos' in s and 'xenos_word' in s
s = s.replace("X360OS Native v7.0", "X360OS Native v8.0")
s = s.replace("X360OS NATIVE v7.0", "X360OS NATIVE v8.0")
out=here/"x360os-ui.c"
out.write_text(s,encoding="utf-8",newline="\n")
print(f"Created {out} ({len(s.splitlines())} lines). No Ubuntu components.")
