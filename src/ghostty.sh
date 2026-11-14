#!/bin/sh
# Starts Ghostty, switching to Mesa software GL when the GPU lacks desktop OpenGL 4.3.
# GHOSTTY_GL_FALLBACK=auto (default) | force | off. An existing LIBGL_ALWAYS_SOFTWARE wins.

libexec=/usr/libexec/ghostty
mode=${GHOSTTY_GL_FALLBACK:-auto}

if [ "$mode" != off ] && [ -z "${LIBGL_ALWAYS_SOFTWARE+x}" ]; then
    status=
    if [ "$mode" = force ]; then
        status=1
    else
        cache=
        if [ -n "${XDG_RUNTIME_DIR:-}" ] && [ -d "$XDG_RUNTIME_DIR" ]; then
            cache="$XDG_RUNTIME_DIR/ghostty-gl-probe"
            [ -r "$cache" ] && status=$(cat "$cache")
        fi
        if [ -z "$status" ]; then
            "$libexec/ghostty-gl-probe"
            status=$?
            [ -n "$cache" ] && printf '%s\n' "$status" >"$cache" 2>/dev/null
        fi
    fi
    if [ "$status" = 1 ]; then
        # the marker lets ghostty drop both variables from its child shells
        export LIBGL_ALWAYS_SOFTWARE=1 GHOSTTY_GL_FALLBACK_ACTIVE=1
    fi
fi

exec "$libexec/ghostty" "$@"
