// Exit 0: desktop OpenGL >= 4.3 core available; 1: desktop GL older than 4.3; 2: undetermined.
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <stdio.h>
#include <string.h>

#ifndef EGL_NO_CONFIG_KHR
#define EGL_NO_CONFIG_KHR ((EGLConfig)0)
#endif

static int has_ext(EGLDisplay dpy, const char *name)
{
    const char *exts = eglQueryString(dpy, EGL_EXTENSIONS);
    return exts && strstr(exts, name) != NULL;
}

static int try_context(EGLDisplay dpy, EGLConfig cfg, const EGLint *attrs)
{
    EGLContext ctx = eglCreateContext(dpy, cfg, EGL_NO_CONTEXT, attrs);
    if (ctx == EGL_NO_CONTEXT)
        return 0;
    eglDestroyContext(dpy, ctx);
    return 1;
}

int main(void)
{
    PFNEGLGETPLATFORMDISPLAYEXTPROC get_display =
        (PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
    if (!get_display)
        return 2;

    EGLDisplay dpy = get_display(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, NULL);
    if (dpy == EGL_NO_DISPLAY || !eglInitialize(dpy, NULL, NULL))
        return 2;

    int result = 2;
    EGLConfig cfg = EGL_NO_CONFIG_KHR;
    if (!eglBindAPI(EGL_OPENGL_API))
        goto out;
    if (!has_ext(dpy, "EGL_KHR_no_config_context")) {
        const EGLint cfg_attrs[] = {EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT, EGL_SURFACE_TYPE, 0, EGL_NONE};
        EGLint n = 0;
        if (!eglChooseConfig(dpy, cfg_attrs, &cfg, 1, &n) || n < 1)
            goto out;
    }

    const EGLint gl43[] = {
        EGL_CONTEXT_MAJOR_VERSION, 4,
        EGL_CONTEXT_MINOR_VERSION, 3,
        EGL_CONTEXT_OPENGL_PROFILE_MASK, EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT,
        EGL_NONE,
    };
    const EGLint any[] = {EGL_NONE};

    if (try_context(dpy, cfg, gl43))
        result = 0;
    else if (try_context(dpy, cfg, any))
        result = 1;

out:
    eglTerminate(dpy);
    return result;
}
