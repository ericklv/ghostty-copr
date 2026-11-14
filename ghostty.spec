# Ghostty with an automatic software-GL fallback for GPUs without desktop OpenGL 4.3.
# Requires network access during %%prep (COPR: enable_net) to fetch Zig and the Zig package cache.

%global appid com.mitchellh.ghostty
# https://github.com/ghostty-org/ghostty/blob/main/PACKAGING.md
%global ghostty_key RWQlAjJC23149WL2sEpT/l0QKy7hMIFhYdQOFy0Z7z7PbneUgvlsnYcV
# https://ziglang.org/download/
%global zig_key RWSGOq2NVecA2UPNdBUZykf1CCb147pkmdtYxgb3Ti+JO/wCYvhbAb/U
%global debug_package %{nil}

Name:           ghostty
Version:        1.4.0
Release:        1%{?dist}
Summary:        Fast, native terminal emulator with a software-GL fallback
License:        MIT AND MPL-2.0 AND OFL-1.1 AND (WTFPL OR CC0-1.0) AND Apache-2.0
URL:            https://ghostty.org/
Source0:        https://release.files.ghostty.org/%{version}/ghostty-%{version}.tar.gz
Source1:        https://release.files.ghostty.org/%{version}/ghostty-%{version}.tar.gz.minisig
Source2:        ghostty.sh
Source3:        ghostty-gl-probe.c

ExclusiveArch:  x86_64 aarch64

BuildRequires:  curl
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  minisign
BuildRequires:  ncurses
BuildRequires:  pandoc-cli
BuildRequires:  systemd-rpm-macros
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  pkgconfig(blueprint-compiler)
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(oniguruma)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(zlib)

Requires:       %{name}-terminfo = %{version}-%{release}
Requires:       (%{name}-kio = %{version}-%{release} if kf6-kio-core)
Requires:       gtk4
Requires:       gtk4-layer-shell
Requires:       libadwaita
Requires:       mesa-dri-drivers
Conflicts:      ghostty-nightly

%description
Ghostty is a fast, feature-rich, and cross-platform terminal emulator that uses
platform-native UI and GPU acceleration.

This build starts Ghostty through a wrapper that probes the GPU once per login
and enables Mesa software rendering (llvmpipe) when desktop OpenGL 4.3 is not
available, e.g. on Mali GPUs driven by Panfrost. Child shells do not inherit it.

%package        bash-completion
Summary:        Ghostty Bash completion
Requires:       %{name} = %{version}-%{release}
Requires:       bash-completion
Supplements:    (%{name} and bash-completion)
BuildArch:      noarch

%description    bash-completion
Bash shell completion for Ghostty.

%package        fish-completion
Summary:        Ghostty Fish completion
Requires:       %{name} = %{version}-%{release}
Requires:       fish
Supplements:    (%{name} and fish)
BuildArch:      noarch

%description    fish-completion
Fish shell completion for Ghostty.

%package        zsh-completion
Summary:        Ghostty Zsh completion
Requires:       %{name} = %{version}-%{release}
Requires:       zsh
Supplements:    (%{name} and zsh)
BuildArch:      noarch

%description    zsh-completion
Zsh shell completion for Ghostty.

%package        devel
Summary:        Development files for Ghostty
Requires:       %{name} = %{version}-%{release}

%description    devel
Development headers for Ghostty.

%package        kio
Summary:        KIO service menu for Ghostty
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description    kio
Dolphin/KIO "Open Ghostty here" service menu.

%package        nautilus
Summary:        Nautilus extension for Ghostty
Requires:       %{name} = %{version}-%{release}
Requires:       nautilus-python
Supplements:    (%{name} and nautilus)
BuildArch:      noarch

%description    nautilus
Nautilus "Open in Ghostty" extension.

%package        vim
Summary:        Vim plugins for Ghostty
Requires:       %{name} = %{version}-%{release}
Requires:       vim-filesystem
Supplements:    (%{name} and vim-filesystem)
BuildArch:      noarch

%description    vim
Vim syntax and filetype plugins for Ghostty configuration files.

%package        neovim
Summary:        Neovim plugins for Ghostty
Requires:       %{name} = %{version}-%{release}
Requires:       neovim
Supplements:    (%{name} and neovim)
BuildArch:      noarch

%description    neovim
Neovim syntax and filetype plugins for Ghostty configuration files.

%package        bat-syntax
Summary:        Bat syntax for Ghostty
Requires:       %{name} = %{version}-%{release}
Requires:       bat
Supplements:    (%{name} and bat)
BuildArch:      noarch

%description    bat-syntax
Bat syntax definition for Ghostty configuration files.

%package        shell-integration
Summary:        Ghostty shell integration
Supplements:    %{name}
BuildArch:      noarch

%description    shell-integration
Shell integration scripts for Ghostty.

%package        terminfo
Summary:        Ghostty terminfo
Requires:       ncurses-term
Supplements:    %{name}
BuildArch:      noarch

%description    terminfo
Ghostty's terminfo entry.

%package -n     libghostty-vt
Summary:        The libghostty-vt library

%description -n libghostty-vt
Terminal emulation library extracted from Ghostty.

%package -n     libghostty-vt-devel
Summary:        Development files for libghostty-vt
Requires:       libghostty-vt = %{version}-%{release}

%description -n libghostty-vt-devel
Headers and pkg-config files for libghostty-vt.

%prep
minisign -V -m %{SOURCE0} -x %{SOURCE1} -P %{ghostty_key}
%autosetup -p1

# keep the software-GL variables out of child shells (inserted after the GSK_RENDERER cleanup)
sed -i -E '/env\.(orderedRemove|remove)\("GSK_RENDERER"\);/{
p
s/^([[:space:]]*)(.*)"GSK_RENDERER"(.*)$/\1if (env.get("GHOSTTY_GL_FALLBACK_ACTIVE") != null) \2"LIBGL_ALWAYS_SOFTWARE"\3/
p
s/^([[:space:]]*)if \(env\.get\("GHOSTTY_GL_FALLBACK_ACTIVE"\) != null\) (.*)"LIBGL_ALWAYS_SOFTWARE"(.*)$/\1\2"GHOSTTY_GL_FALLBACK_ACTIVE"\3/
}' src/apprt/gtk/class/surface.zig
grep -q '"GHOSTTY_GL_FALLBACK_ACTIVE") != null' src/apprt/gtk/class/surface.zig

# official Zig release matching build.zig.zon, verified with the Zig signing key
zig_version=$(sed -n 's/.*minimum_zig_version = "\([^"]*\)".*/\1/p' build.zig.zon)
zig_name="zig-%{_arch}-linux-${zig_version}"
curl -fsSLO "https://ziglang.org/download/${zig_version}/${zig_name}.tar.xz"
curl -fsSLO "https://ziglang.org/download/${zig_version}/${zig_name}.tar.xz.minisig"
minisign -V -m "${zig_name}.tar.xz" -x "${zig_name}.tar.xz.minisig" -P %{zig_key}
tar -xf "${zig_name}.tar.xz"
mv "${zig_name}" .zig
rm -f "${zig_name}.tar.xz" "${zig_name}.tar.xz.minisig"

export ZIG_GLOBAL_CACHE_DIR="$PWD/.zig-cache-global"
PATH="$PWD/.zig:$PATH" ./nix/build-support/fetch-zig-cache.sh

# zig >= 0.17 caches packages as <hash>.tar.gz, but --system needs extracted <hash>/ dirs;
# strip the <hash>/ prefix, then unwrap single-directory wrappers (upstream tarball roots)
for f in "$ZIG_GLOBAL_CACHE_DIR"/p/*.tar.gz; do
    d="${f%.tar.gz}"
    tmp=$(mktemp -d)
    tar -xzf "$f" -C "$tmp" --strip-components=1
    root="$tmp"
    while [ "$(ls -A "$root" | wc -l)" -eq 1 ] && [ -d "$root/$(ls -A "$root")" ]; do
        root="$root/$(ls -A "$root")"
    done
    mv "$root" "$d"
    rm -rf "$tmp" "$f"
done

%build
gcc %{optflags} -o ghostty-gl-probe %{SOURCE3} %{build_ldflags} -lEGL

%install
export ZIG_GLOBAL_CACHE_DIR="$PWD/.zig-cache-global"
export ZIG_LOCAL_CACHE_DIR="$PWD/.zig-cache"
DESTDIR=%{buildroot} ./.zig/zig build \
    --prefix %{_prefix} \
    --prefix-lib-dir %{_lib} \
    --system "$ZIG_GLOBAL_CACHE_DIR/p" \
    -fno-sys=glslang -fno-sys=spirv-cross -fno-sys=simdutf -fno-sys=highway \
    -Demit-exe=true \
    -Dinstalled-exe-path=%{_bindir}/%{name} \
    -Doptimize=ReleaseFast \
    -Dcpu=baseline \
    -Dpie=true \
    -Dstrip=false \
    -Demit-docs \
    -Demit-themes=false \
    -Dversion-string=%{version}

# real binary in libexec, wrapper as the public entry point
install -d %{buildroot}%{_libexecdir}/%{name}
mv %{buildroot}%{_bindir}/%{name} %{buildroot}%{_libexecdir}/%{name}/%{name}
install -pm 0755 ghostty-gl-probe %{buildroot}%{_libexecdir}/%{name}/ghostty-gl-probe
install -pm 0755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# upstream writes DESTDIR into prefix and hardcodes lib/
sed -i -e 's|%{buildroot}||g' -e 's|^libdir=.*|libdir=%{_libdir}|' %{buildroot}%{_datadir}/pkgconfig/libghostty-vt*.pc

# zig's static archive breaks brp-strip-lto; only the shared library is shipped
rm -f %{buildroot}%{_libdir}/libghostty-vt.a %{buildroot}%{_datadir}/pkgconfig/libghostty-vt-static.pc

# provided by ncurses-term on current Fedora
rm -f %{buildroot}%{_datadir}/terminfo/g/%{name}

%find_lang %{appid}

%post
%systemd_user_post app-%{appid}.service

%preun
%systemd_user_preun app-%{appid}.service

%postun
%systemd_user_postun app-%{appid}.service

%files -f %{appid}.lang
%doc README.md
%license LICENSE
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/dbus-1/services/%{appid}.service
%{_datadir}/%{name}/doc/
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_mandir}/man1/%{name}.1*
%{_mandir}/man5/%{name}.5*
%{_userunitdir}/app-%{appid}.service

%files bash-completion
%{bash_completions_dir}/%{name}.bash

%files fish-completion
%{fish_completions_dir}/%{name}.fish

%files zsh-completion
%{zsh_completions_dir}/_%{name}

%files devel
%{_includedir}/ghostty/

%files kio
%{_datadir}/kio/servicemenus/%{appid}.desktop

%files nautilus
%{_datadir}/nautilus-python/extensions/%{name}.py

%files vim
%{_datadir}/vim/vimfiles/*/%{name}.vim

%files neovim
%{_datadir}/nvim/site/*/%{name}.vim

%files bat-syntax
%{_datadir}/bat/syntaxes/%{name}.sublime-syntax

%files shell-integration
%{_datadir}/%{name}/shell-integration/

%files terminfo
%{_datadir}/terminfo/x/xterm-%{name}

%files -n libghostty-vt
%{_libdir}/libghostty-vt.so.*

%files -n libghostty-vt-devel
%{_libdir}/libghostty-vt.so
%{_datadir}/pkgconfig/libghostty-vt.pc

%changelog
* Sat Nov 14 2026 ericklv - 1.4.0-1
- Software-GL fallback wrapper for GPUs without desktop OpenGL 4.3
