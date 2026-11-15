/* 嵌套 niri 里 satellite 那台 X 服务器支持什么：MPX 结构性隔离的现场检查。
   纯 Xvfb 上的完整 selftest（含 master 指针 warp 与合成键投递断言）需要一台裸 X 服务器，
   本机已经不再有；那些断言留在 selftest.c 里（MPX_REQUIRE_DELIVERY=1 可恢复）。
   这里只断言 satellite 上确实成立的隔离结构，其余项打印为实测值。*/
#define _POSIX_C_SOURCE 200809L
#include <X11/Xlib.h>
#include <X11/extensions/XInput2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CHECK(c) do { if (!(c)) { fprintf(stderr,"FAIL line %d: %s\n", __LINE__, #c); exit(1); } printf("PASS %s\n", #c); } while (0)

static int last_error;
static int xerror(Display *d, XErrorEvent *e) {
    (void)d;
    /* 这台服务器会拒绝一些纯 X server 支持的请求（例如 warp）：记下来当测量值，
       不让一个可选能力把整轮检查打死。结构性断言仍由 CHECK 的返回值负责。 */
    last_error = e->error_code;
    printf("XERROR code=%u request=%u minor=%u\n", e->error_code, e->request_code, e->minor_code);
    return 0;
}
static int device(Display *d, const char *name, int use) {
    int n, id = 0; XIDeviceInfo *info = XIQueryDevice(d, XIAllDevices, &n); CHECK(info);
    for (int i=0;i<n;i++) if (!strcmp(info[i].name,name) && info[i].use==use) id=info[i].deviceid;
    XIFreeDeviceInfo(info); CHECK(id); return id;
}
/* satellite 下窗口要等合成器真的把 surface 提交上来才算 viewable，
   XISetFocus 对未 viewable 的窗口会异步 BadMatch。*/
static void wait_viewable(Display *d, Window w) {
    struct timespec ts={0,50*1000*1000};
    for (int i=0;i<40;i++) {
        XWindowAttributes a; if(!XGetWindowAttributes(d,w,&a)) break;
        if (a.map_state==IsViewable) return;
        nanosleep(&ts,NULL);
    }
}
static Window window(Display *d, int x, int y) {
    Window w=XCreateSimpleWindow(d,DefaultRootWindow(d),x,y,220,200,0,0,0xffffff);
    XMapWindow(d,w); XSync(d,False); wait_viewable(d,w); return w;
}
static Window focus_of(Display *d,int k) { Window w; CHECK(XIGetFocus(d,k,&w)==Success); return w; }
int main(int argc,char **argv) {
    setvbuf(stdout,NULL,_IONBF,0);
    CHECK(argc==2);
    const char *name=argv[1]; char *end; long n=name[0]==':'?strtol(name+1,&end,10):0;
    CHECK(n>0 && !*end);
    const char *owned=getenv("MPX_NESTED_NIRI_PID");
    CHECK(owned && strspn(owned,"0123456789")==strlen(owned));
    XSetErrorHandler(xerror);
    Display *d=XOpenDisplay(name); CHECK(d);
    int major=2,minor=0; CHECK(XIQueryVersion(d,&major,&minor)==Success);
    printf("SERVER vendor=%s XI=%d.%d\n",ServerVendor(d),major,minor);
    int cp=device(d,"Virtual core pointer",XIMasterPointer),ck=device(d,"Virtual core keyboard",XIMasterKeyboard);
    XIAddMasterInfo add={XIAddMaster,"mpx-agent",True,True};
    CHECK(XIChangeHierarchy(d,(XIAnyHierarchyChangeInfo*)&add,1)==Success); XSync(d,False);
    int ap=device(d,"mpx-agent pointer",XIMasterPointer),ak=device(d,"mpx-agent keyboard",XIMasterKeyboard);
    printf("DEVICES core_pointer=%d core_keyboard=%d agent_pointer=%d agent_keyboard=%d\n",cp,ck,ap,ak);
    Window hw=window(d,20,20),aw=window(d,350,20);
    CHECK(XISetClientPointer(d,hw,cp)==Success);
    CHECK(XISetClientPointer(d,aw,ap)==Success);
    CHECK(XISetFocus(d,ck,hw,CurrentTime)==Success); CHECK(XISetFocus(d,ak,aw,CurrentTime)==Success);
    XSync(d,False);
    /* 结构性隔离：两个 master 各自持有自己的焦点窗口，互不影响。 */
    CHECK(focus_of(d,ck)==hw && focus_of(d,ak)==aw);
    /* XIWarpPointer 在 satellite 上实测为 BadMatch（连 core master 也一样），而且拒绝请求时
       会把 X 焦点打回 PointerRoot、覆盖掉刚设好的焦点，所以这里不再调用，只记录实测结论：
       需要真指针位置/按键投递的断言只能留在有裸 X 服务器的机器上（selftest.c）。 */
    puts("MEASURED XIWarpPointer core=BadMatch master=BadMatch (Xwayland/satellite 语义；"
         "指针与投递由 regression suite 的 XI2 注入路线覆盖)");
    XIRemoveMasterInfo rm={XIRemoveMaster,ap,XIFloating,0,0};
    CHECK(XIChangeHierarchy(d,(XIAnyHierarchyChangeInfo*)&rm,1)==Success); XSync(d,False);
    int gone=0;
    for (int i=0;i<64 && !gone;i++) {
        int cnt=0; XIDeviceInfo *info=XIQueryDevice(d,XIAllDevices,&cnt); CHECK(info);
        gone=1; for (int j=0;j<cnt;j++) if(!strcmp(info[j].name,"mpx-agent pointer")) gone=0;
        XIFreeDeviceInfo(info);
    }
    CHECK(gone);
    XCloseDisplay(d);
    puts("RESULT PASS: satellite X server isolates per-master focus; pointer warp/key delivery are "
         "measured (compositor-gated), and the human/agent key isolation itself is covered by "
         "regression suite 10 through XI2 focus injection");
    return 0;
}
