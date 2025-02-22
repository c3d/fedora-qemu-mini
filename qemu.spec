%ifarch %{ix86}
%global kvm_arch   x86
# need_qemu_kvm should only ever be used by x86
%global need_qemu_kvm 1
%endif
%ifarch x86_64
%global kvm_arch   x86
# need_qemu_kvm should only ever be used by x86
%global need_qemu_kvm 1
%endif
%ifarch %{power64}
%global kvm_arch   ppc
%endif
%ifarch s390x
%global kvm_arch   s390x
%endif
%ifarch armv7hl
%global kvm_arch   arm
%endif
%ifarch aarch64
%global kvm_arch   aarch64
%endif
%ifarch %{mips}
%global kvm_arch   mips
%endif

%global user_static 1
%global user_mini 0

%global have_kvm 0
%if 0%{?kvm_arch:1}
%global kvm_package system-%{kvm_arch}
%global have_kvm 1
%global user_mini 1
%endif

# Matches numactl ExcludeArch
%global have_numactl 1
%ifarch s390 %{arm}
%global have_numactl 0
%endif

# Upstream disables iasl for big endian and QEMU checks
# for this. Fedora has re-enabled it on BE circumventing
# the QEMU checks, but it fails none the less:
#
# https://bugzilla.redhat.com/show_bug.cgi?id=1332449
%global have_iasl 1
%ifnarch s390 s390x ppc ppc64
%global have_iasl 0
%endif

# Matches spice ExclusiveArch
%global have_spice 0
%ifarch %{ix86} x86_64 %{arm} aarch64
%global have_spice 1
%endif

# Matches xen ExclusiveArch
%global have_xen 0
%ifarch %{ix86} x86_64 armv7hl aarch64
%global have_xen 1
%endif

# Matches edk2.spec ExclusiveArch
%global have_edk2 0
%ifarch %{ix86} x86_64 %{arm} aarch64
%global have_edk2 1
%endif

# If we can run qemu-sanity-check, hostqemu gets defined.
%ifarch %{arm}
%global hostqemu arm-softmmu/qemu-system-arm
%endif
%ifarch aarch64
%global hostqemu arm-softmmu/qemu-system-aarch64
%endif
%ifarch %{ix86}
%global hostqemu i386-softmmu/qemu-system-i386
%endif
%ifarch x86_64
%global hostqemu x86_64-softmmu/qemu-system-x86_64
%endif

# All modules should be listed here.
%ifarch %{ix86} %{arm}
%define with_block_rbd 0
%else
%define with_block_rbd 1
%endif
%global with_block_gluster 1

%define evr %{epoch}:%{version}-%{release}

%define requires_block_curl Requires: %{name}-block-curl = %{evr}
%define requires_block_dmg Requires: %{name}-block-dmg = %{evr}
%if %{with_block_gluster}
%define requires_block_gluster Requires: %{name}-block-gluster = %{evr}
%define obsoletes_block_gluster %{nil}
%else
%define requires_block_gluster %{nil}
%define obsoletes_block_gluster Obsoletes: %{name}-block-gluster < %{evr}
%endif
%define requires_block_iscsi Requires: %{name}-block-iscsi = %{evr}
%define requires_block_nfs Requires: %{name}-block-nfs = %{evr}
%if %{with_block_rbd}
%define requires_block_rbd Requires: %{name}-block-rbd = %{evr}
%define obsoletes_block_rbd %{nil}
%else
%define requires_block_rbd %{nil}
%define obsoletes_block_rbd Obsoletes: %{name}-block-rbd < %{evr}
%endif
%define requires_block_ssh Requires: %{name}-block-ssh = %{evr}
%define requires_audio_alsa Requires: %{name}-audio-alsa = %{evr}
%define requires_audio_oss Requires: %{name}-audio-oss = %{evr}
%define requires_audio_pa Requires: %{name}-audio-pa = %{evr}
%define requires_audio_sdl Requires: %{name}-audio-sdl = %{evr}
%define requires_ui_curses Requires: %{name}-ui-curses = %{evr}
%define requires_ui_gtk Requires: %{name}-ui-gtk = %{evr}
%define requires_ui_sdl Requires: %{name}-ui-sdl = %{evr}

%global requires_all_modules \
%{requires_block_curl} \
%{requires_block_dmg} \
%{requires_block_gluster} \
%{requires_block_iscsi} \
%{requires_block_nfs} \
%{requires_block_rbd} \
%{requires_block_ssh} \
%{requires_audio_alsa} \
%{requires_audio_oss} \
%{requires_audio_pa} \
%{requires_audio_sdl} \
%{requires_ui_curses} \
%{requires_ui_gtk} \
%{requires_ui_sdl}

# Modules which can be conditionally built
%global obsoletes_some_modules \
%{obsoletes_block_gluster} \
%{obsoletes_block_rbd}

# Release candidate version tracking
#global rcver rc2
%if 0%{?rcver:1}
%global rcrel .%{rcver}
%global rcstr -%{rcver}
%endif


Summary: QEMU is a FAST! processor emulator
Name: qemu
Version: 4.1.0
Release: 1%{?rcrel}%{?dist}.2
Epoch: 2
License: GPLv2 and BSD and MIT and CC-BY
URL: http://www.qemu.org/

Source0: http://wiki.qemu-project.org/download/%{name}-%{version}%{?rcstr}.tar.xz

# guest agent service
Source10: qemu-guest-agent.service
Source17: qemu-ga.sysconfig
# guest agent udev rules
Source11: 99-qemu-guest-agent.rules
# /etc/qemu/bridge.conf
Source12: bridge.conf
# qemu-kvm back compat wrapper installed as /usr/bin/qemu-kvm
Source13: qemu-kvm.sh
# PR manager service
Source14: qemu-pr-helper.service
Source15: qemu-pr-helper.socket
# /etc/modprobe.d/kvm.conf, for x86
Source20: kvm-x86.modprobe.conf
# /etc/security/limits.d/95-kvm-ppc64-memlock.conf
Source21: 95-kvm-ppc64-memlock.conf


# documentation deps
BuildRequires: texinfo
# For /usr/bin/pod2man
BuildRequires: perl-podlators
%ifnarch %{ix86}
# For sanity test
BuildRequires: qemu-sanity-check-nodeps
BuildRequires: kernel
%endif
%if %{have_iasl}
# For acpi compilation
BuildRequires: iasl
%endif
# For chrpath calls in specfile
BuildRequires: chrpath

# -display sdl support
BuildRequires: SDL2-devel
# used in various places for compression
BuildRequires: zlib-devel
# used in various places for crypto
BuildRequires: gnutls-devel
# VNC sasl auth support
BuildRequires: cyrus-sasl-devel
# aio implementation for block drivers
BuildRequires: libaio-devel
# pulseaudio audio output
BuildRequires: pulseaudio-libs-devel
# alsa audio output
BuildRequires: alsa-lib-devel
# qemu-pr-helper multipath support (requires libudev too)
BuildRequires: device-mapper-multipath-devel
BuildRequires: systemd-devel
# iscsi drive support
BuildRequires: libiscsi-devel
# NFS drive support
BuildRequires: libnfs-devel
# snappy compression for memory dump
BuildRequires: snappy-devel
# lzo compression for memory dump
BuildRequires: lzo-devel
# needed for -display curses
BuildRequires: ncurses-devel
# used by 9pfs
BuildRequires: libattr-devel
BuildRequires: libcap-devel
# used by qemu-bridge-helper and qemu-pr-helper
BuildRequires: libcap-ng-devel
# spice usb redirection support
BuildRequires: usbredir-devel >= 0.5.2
%if %{have_spice}
# spice graphics support
BuildRequires: spice-protocol >= 0.12.2
BuildRequires: spice-server-devel >= 0.12.0
%endif
# seccomp containment support
BuildRequires: libseccomp-devel >= 2.3.0
# For network block driver
BuildRequires: libcurl-devel
%if %{with_block_rbd}
# For rbd block driver
BuildRequires: librados2-devel
BuildRequires: librbd1-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# For VNC JPEG support
BuildRequires: libjpeg-devel
# For VNC PNG support
BuildRequires: libpng-devel
# For BlueZ device support
BuildRequires: bluez-libs-devel
# For Braille device support
BuildRequires: brlapi-devel
# For FDT device tree support
BuildRequires: libfdt-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
%if %{with_block_gluster}
# For gluster support
BuildRequires: glusterfs-devel >= 3.4.0
BuildRequires: glusterfs-api-devel >= 3.4.0
%endif
# Needed for usb passthrough for qemu >= 1.5
BuildRequires: libusbx-devel
# SSH block driver
BuildRequires: libssh-devel
# GTK frontend
BuildRequires: gtk3-devel
BuildRequires: vte291-devel
# GTK translations
BuildRequires: gettext
# RDMA migration
BuildRequires: rdma-core-devel
%if %{have_xen}
# Xen support
BuildRequires: xen-devel
%endif
%if %{have_numactl}
# qemu 2.1: needed for memdev hostmem backend
BuildRequires: numactl-devel
%endif
# qemu 2.3: reading bzip2 compressed dmg images
BuildRequires: bzip2-devel
# qemu 2.4: needed for opengl bits
BuildRequires: libepoxy-devel
# qemu 2.5: needed for TLS test suite
BuildRequires: libtasn1-devel
# qemu 2.5: libcacard is it's own project now
BuildRequires: libcacard-devel >= 2.5.0
# qemu 2.5: virgl 3d support
BuildRequires: virglrenderer-devel
# qemu 2.6: Needed for gtk GL support, vhost-user-gpu
BuildRequires: mesa-libgbm-devel
# qemu 2.11: preferred disassembler for TCG
BuildRequires: capstone-devel
# qemu 2.12: parallels disk images require libxml2 now
BuildRequires: libxml2-devel
%ifarch x86_64
# qemu 3.1: Used for nvdimm
BuildRequires: libpmem-devel
%endif
# qemu 3.1: Used for qemu-ga
BuildRequires: libudev-devel
# qemu 4.0: Use for qauth infrastructure
BuildRequires: pam-devel
# qemu 4.0: user-mode networking
%if 0%{?fedora} > 30
BuildRequires: libslirp-devel
%endif
# qemu 4.0: sphinx-build used for some docs
%if 0%{?fedora} > 30
BuildRequires: python3-sphinx
%else
BuildRequires: python2-sphinx
%endif
# qemu 4.0: Used by test suite ./scripts/tap-driver.pl
BuildRequires: perl-Test-Harness
# Required for making python shebangs versioned
BuildRequires: /usr/bin/pathfix.py
BuildRequires: python3-devel

BuildRequires: glibc-static pcre-static glib2-static zlib-static

%if 0%{?hostqemu:1}
# For complicated reasons, this is required so that
# /bin/kernel-install puts the kernel directly into /boot, instead of
# into a /boot/<machine-id> subdirectory (in Fedora >= 23).  This is
# so we can run qemu-sanity-check.  Read the kernel-install script to
# understand why.
BuildRequires: grubby
%endif

Requires: %{name}-user = %{epoch}:%{version}-%{release}
Requires: %{name}-system-aarch64 = %{epoch}:%{version}-%{release}
Requires: %{name}-system-alpha = %{epoch}:%{version}-%{release}
Requires: %{name}-system-arm = %{epoch}:%{version}-%{release}
Requires: %{name}-system-cris = %{epoch}:%{version}-%{release}
Requires: %{name}-system-lm32 = %{epoch}:%{version}-%{release}
Requires: %{name}-system-m68k = %{epoch}:%{version}-%{release}
Requires: %{name}-system-microblaze = %{epoch}:%{version}-%{release}
Requires: %{name}-system-mips = %{epoch}:%{version}-%{release}
Requires: %{name}-system-moxie = %{epoch}:%{version}-%{release}
Requires: %{name}-system-nios2 = %{epoch}:%{version}-%{release}
Requires: %{name}-system-or1k = %{epoch}:%{version}-%{release}
Requires: %{name}-system-ppc = %{epoch}:%{version}-%{release}
Requires: %{name}-system-riscv = %{epoch}:%{version}-%{release}
Requires: %{name}-system-s390x = %{epoch}:%{version}-%{release}
Requires: %{name}-system-sh4 = %{epoch}:%{version}-%{release}
Requires: %{name}-system-sparc = %{epoch}:%{version}-%{release}
Requires: %{name}-system-tricore = %{epoch}:%{version}-%{release}
Requires: %{name}-system-unicore32 = %{epoch}:%{version}-%{release}
Requires: %{name}-system-x86 = %{epoch}:%{version}-%{release}
Requires: %{name}-system-xtensa = %{epoch}:%{version}-%{release}
Requires: %{name}-img = %{epoch}:%{version}-%{release}


%description
QEMU is a generic and open source processor emulator which achieves a good
emulation speed by using dynamic translation. QEMU has two operating modes:

 * Full system emulation. In this mode, QEMU emulates a full system (for
   example a PC), including a processor and various peripherials. It can be
   used to launch different Operating Systems without rebooting the PC or
   to debug system code.
 * User mode emulation. In this mode, QEMU can launch Linux processes compiled
   for one CPU on another CPU.

As QEMU requires no host kernel patches to run, it is safe and easy to use.


%package  common
Summary: QEMU common files needed by all QEMU targets
Requires: ipxe-roms-qemu
Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%{obsoletes_some_modules}
%description common
This package provides the common files needed by all QEMU targets


%package guest-agent
Summary: QEMU guest agent
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%description guest-agent
This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.


%package  img
Summary: QEMU command line tool for manipulating disk images
%description img
This package provides a command line tool for manipulating disk images


%package -n ivshmem-tools
Summary: Client and server for QEMU ivshmem device
%description -n ivshmem-tools
This package provides client and server tools for QEMU's ivshmem device.


%package  block-curl
Summary: QEMU CURL block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-curl
This package provides the additional CURL block driver for QEMU.

Install this package if you want to access remote disks over
http, https, ftp and other transports provided by the CURL library.


%package  block-dmg
Summary: QEMU block driver for DMG disk images
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-dmg
This package provides the additional DMG block driver for QEMU.

Install this package if you want to open '.dmg' files.


%if %{with_block_gluster}
%package  block-gluster
Summary: QEMU Gluster block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-gluster
This package provides the additional Gluster block driver for QEMU.

Install this package if you want to access remote Gluster storage.
%endif


%package  block-iscsi
Summary: QEMU iSCSI block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-iscsi
This package provides the additional iSCSI block driver for QEMU.

Install this package if you want to access iSCSI volumes.


%package  block-nfs
Summary: QEMU NFS block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}

%description block-nfs
This package provides the additional NFS block driver for QEMU.

Install this package if you want to access remote NFS storage.


%if %{with_block_rbd}
%package  block-rbd
Summary: QEMU Ceph/RBD block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-rbd
This package provides the additional Ceph/RBD block driver for QEMU.

Install this package if you want to access remote Ceph volumes
using the rbd protocol.
%endif

%package  block-ssh
Summary: QEMU SSH block driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-ssh
This package provides the additional SSH block driver for QEMU.

Install this package if you want to access remote disks using
the Secure Shell (SSH) protocol.


%package  audio-alsa
Summary: QEMU ALSA audio driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description audio-alsa
This package provides the additional ALSA audio driver for QEMU.

%package  audio-oss
Summary: QEMU OSS audio driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description audio-oss
This package provides the additional OSS audio driver for QEMU.

%package  audio-pa
Summary: QEMU PulseAudio audio driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description audio-pa
This package provides the additional PulseAudi audio driver for QEMU.

%package  audio-sdl
Summary: QEMU SDL audio driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description audio-sdl
This package provides the additional SDL audio driver for QEMU.


%package  ui-curses
Summary: QEMU curses UI driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description ui-curses
This package provides the additional curses UI for QEMU.

%package  ui-gtk
Summary: QEMU GTK UI driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description ui-gtk
This package provides the additional GTK UI for QEMU.

%package  ui-sdl
Summary: QEMU SDL UI driver
Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description ui-sdl
This package provides the additional SDL UI for QEMU.


%if %{have_kvm}
%package kvm
Summary: QEMU metapackage for KVM support
Requires: qemu-%{kvm_package} = %{epoch}:%{version}-%{release}
%description kvm
This is a meta-package that provides a qemu-system-<arch> package for native
architectures where kvm can be enabled. For example, in an x86 system, this
will install qemu-system-x86


%package kvm-core
Summary: QEMU metapackage for KVM support
Requires: qemu-%{kvm_package}-core = %{epoch}:%{version}-%{release}
%description kvm-core
This is a meta-package that provides a qemu-system-<arch>-core package
for native architectures where kvm can be enabled. For example, in an
x86 system, this will install qemu-system-x86-core


%package mini
Summary: Minimum QEMU with KVM support but no legacy
Requires: qemu-%{kvm_package}-mini = %{epoch}:%{version}-%{release}
%description mini
This is a meta-package that provides a qemu-system-<arch>-mini package
containing a stripped-down build of QEMU system emulator that only
targets a minimal modern feature set, without legacy drivers. For
example, on an x86 system, this will install qemu-system-x86-mini.
%endif


%package user
Summary: QEMU user mode emulation of qemu targets
Requires: %{name}-common = %{epoch}:%{version}-%{release}
# On upgrade, make qemu-user get replaced with qemu-user + qemu-user-binfmt
Obsoletes: %{name}-user < 2:2.6.0-5%{?dist}
%description user
This package provides the user mode emulation of qemu targets


%package user-binfmt
Summary: QEMU user mode emulation of qemu targets
Requires: %{name}-user = %{epoch}:%{version}-%{release}
Requires(post): systemd-units
Requires(postun): systemd-units
# qemu-user-binfmt + qemu-user-static both provide binfmt rules
Conflicts: %{name}-user-static
# On upgrade, make qemu-user get replaced with qemu-user + qemu-user-binfmt
Obsoletes: %{name}-user < 2:2.6.0-5%{?dist}
%description user-binfmt
This package provides the user mode emulation of qemu targets

%if %{user_static}
%package user-static
Summary: QEMU user mode emulation of qemu targets static build
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires(post): systemd-units
Requires(postun): systemd-units
# qemu-user-binfmt + qemu-user-static both provide binfmt rules
Conflicts: %{name}-user-binfmt
Provides: %{name}-user-binfmt
%description user-static
This package provides the user mode emulation of qemu targets built as
static binaries
%endif


%package system-aarch64
Summary: QEMU system emulator for AArch64
Requires: %{name}-system-aarch64-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-aarch64
This package provides the QEMU system emulator for AArch64.

%package system-aarch64-core
Summary: QEMU system emulator for AArch64
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%if %{have_edk2}
Requires: edk2-aarch64
%endif
%description system-aarch64-core
This package provides the QEMU system emulator for AArch64.

%ifarch aarch64
%package system-aarch64-mini
Summary: QEMU system emulator for AArch64 in a minimal configuration
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%if %{have_edk2}
Requires: edk2-aarch64
%endif
%description system-aarch64-mini
This package provides the QEMU system emulator for AArch64 in a
minimal configuration suitable for use with modern Linux kernels.
%endif

%package system-alpha
Summary: QEMU system emulator for Alpha
Requires: %{name}-system-alpha-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-alpha
This package provides the QEMU system emulator for Alpha systems.

%package system-alpha-core
Summary: QEMU system emulator for Alpha
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-alpha-core
This package provides the QEMU system emulator for Alpha systems.


%package system-arm
Summary: QEMU system emulator for ARM
Requires: %{name}-system-arm-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-arm
This package provides the QEMU system emulator for ARM systems.

%package system-arm-core
Summary: QEMU system emulator for ARM
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-arm-core
This package provides the QEMU system emulator for ARM boards.

%ifarch %{arm}
%package system-arm-mini
Summary: QEMU system emulator for ARM in a minimal configuration
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-arm-mini
This package provides the QEMU system emulator for ARM boards in a
minimal configuration suitable for use with modern Linux kernels.
%endif

%package system-cris
Summary: QEMU system emulator for CRIS
Requires: %{name}-system-cris-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-cris
This package provides the system emulator for CRIS systems.

%package system-cris-core
Summary: QEMU system emulator for CRIS
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-cris-core
This package provides the system emulator for CRIS boards.


%package system-hppa
Summary: QEMU system emulator for HPPA
Requires: %{name}-system-hppa-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-hppa
This package provides the QEMU system emulator for HPPA.

%package system-hppa-core
Summary: QEMU system emulator for hppa
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-hppa-core
This package provides the QEMU system emulator for HPPA.


%package system-lm32
Summary: QEMU system emulator for LatticeMico32
Requires: %{name}-system-lm32-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-lm32
This package provides the QEMU system emulator for LatticeMico32 boards.

%package system-lm32-core
Summary: QEMU system emulator for LatticsMico32
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-lm32-core
This package provides the QEMU system emulator for LatticeMico32 boards.


%package system-m68k
Summary: QEMU system emulator for ColdFire (m68k)
Requires: %{name}-system-m68k-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-m68k
This package provides the QEMU system emulator for ColdFire boards.

%package system-m68k-core
Summary: QEMU system emulator for ColdFire (m68k)
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-m68k-core
This package provides the QEMU system emulator for ColdFire boards.


%package system-microblaze
Summary: QEMU system emulator for Microblaze
Requires: %{name}-system-microblaze-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-microblaze
This package provides the QEMU system emulator for Microblaze boards.

%package system-microblaze-core
Summary: QEMU system emulator for Microblaze
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-microblaze-core
This package provides the QEMU system emulator for Microblaze boards.


%package system-mips
Summary: QEMU system emulator for MIPS
Requires: %{name}-system-mips-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-mips
This package provides the QEMU system emulator for MIPS systems.

%package system-mips-core
Summary: QEMU system emulator for MIPS
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-mips-core
This package provides the QEMU system emulator for MIPS systems.


%package system-moxie
Summary: QEMU system emulator for Moxie
Requires: %{name}-system-moxie-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-moxie
This package provides the QEMU system emulator for Moxie boards.

%package system-moxie-core
Summary: QEMU system emulator for Moxie
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-moxie-core
This package provides the QEMU system emulator for Moxie boards.


%package system-nios2
Summary: QEMU system emulator for nios2
Requires: %{name}-system-nios2-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-nios2
This package provides the QEMU system emulator for NIOS2.

%package system-nios2-core
Summary: QEMU system emulator for nios2
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-nios2-core
This package provides the QEMU system emulator for NIOS2.


%package system-or1k
Summary: QEMU system emulator for OpenRisc32
Requires: %{name}-system-or1k-core = %{epoch}:%{version}-%{release}
Obsoletes: %{name}-system-or32 < 2:2.9.0
%{requires_all_modules}
%description system-or1k
This package provides the QEMU system emulator for OpenRisc32 boards.

%package system-or1k-core
Summary: QEMU system emulator for OpenRisc32
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Obsoletes: %{name}-system-or32-core < 2:2.9.0
%description system-or1k-core
This package provides the QEMU system emulator for OpenRisc32 boards.


%package system-ppc
Summary: QEMU system emulator for PPC
Requires: %{name}-system-ppc-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-ppc
This package provides the QEMU system emulator for PPC and PPC64 systems.

%package system-ppc-core
Summary: QEMU system emulator for PPC
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: openbios
Requires: SLOF
Requires: seavgabios-bin
%description system-ppc-core
This package provides the QEMU system emulator for PPC and PPC64 systems.

%ifarch %{power64}
%package system-ppc-mini
Summary: QEMU system emulator for PPC in a minimal configuration
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: openbios
Requires: SLOF
Requires: seavgabios-bin
%description system-ppc-mini
This package provides the QEMU system emulator for PPC and PPC64
systems in a minimal configuration suitable for use with modern Linux
kernels.
%endif

%package system-riscv
Summary: QEMU system emulator for RISC-V
Requires: %{name}-system-riscv-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-riscv
This package provides the QEMU system emulator for RISC-V systems.

%package system-riscv-core
Summary: QEMU system emulator for RISC-V
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-riscv-core
This package provides the QEMU system emulator for RISC-V systems.


%package system-s390x
Summary: QEMU system emulator for S390
Requires: %{name}-system-s390x-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-s390x
This package provides the QEMU system emulator for S390 systems.

%package system-s390x-core
Summary: QEMU system emulator for S390
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-s390x-core
This package provides the QEMU system emulator for S390 systems.

%ifarch s390x
%package system-s390x-mini
Summary: QEMU system emulator for S390 in a minimal configuration
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-s390x-mini
This package provides the QEMU system emulator for S390 systems in a
minimal configuration suitable for use with modern Linux kernels.
%endif


%package system-sh4
Summary: QEMU system emulator for SH4
Requires: %{name}-system-sh4-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-sh4
This package provides the QEMU system emulator for SH4 boards.

%package system-sh4-core
Summary: QEMU system emulator for SH4
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-sh4-core
This package provides the QEMU system emulator for SH4 boards.


%package system-sparc
Summary: QEMU system emulator for SPARC
Requires: %{name}-system-sparc-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-sparc
This package provides the QEMU system emulator for SPARC and SPARC64 systems.

%package system-sparc-core
Summary: QEMU system emulator for SPARC
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: openbios
%description system-sparc-core
This package provides the QEMU system emulator for SPARC and SPARC64 systems.


%package system-tricore
Summary: QEMU system emulator for tricore
Requires: %{name}-system-tricore-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-tricore
This package provides the QEMU system emulator for Tricore.

%package system-tricore-core
Summary: QEMU system emulator for tricore
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-tricore-core
This package provides the QEMU system emulator for Tricore.


%package system-unicore32
Summary: QEMU system emulator for Unicore32
Requires: %{name}-system-unicore32-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-unicore32
This package provides the QEMU system emulator for Unicore32 boards.

%package system-unicore32-core
Summary: QEMU system emulator for Unicore32
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-unicore32-core
This package provides the QEMU system emulator for Unicore32 boards.


%package system-x86
Summary: QEMU system emulator for x86
Requires: %{name}-system-x86-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-x86
This package provides the QEMU system emulator for x86. When being run in a x86
machine that supports it, this package also provides the KVM virtualization
platform.

%package system-x86-core
Summary: QEMU system emulator for x86
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: seabios-bin
Requires: sgabios-bin
Requires: seavgabios-bin
%if %{have_edk2}
Requires: edk2-ovmf
%endif
%description system-x86-core
This package provides the QEMU system emulator for x86. When being run in a x86
machine that supports it, this package also provides the KVM virtualization
platform.

%ifarch x86_64
%package system-x86-mini
Summary: QEMU system emulator for x86 in a minimal configuration
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: seabios-bin
Requires: sgabios-bin
Requires: seavgabios-bin
%if %{have_edk2}
Requires: edk2-ovmf
%endif
%description system-x86-mini
This package provides the QEMU system emulator for x86 in a minimal
configuration suitable for use with modern Linux kernels.
%endif

%package system-xtensa
Summary: QEMU system emulator for Xtensa
Requires: %{name}-system-xtensa-core = %{epoch}:%{version}-%{release}
%{requires_all_modules}
%description system-xtensa
This package provides the QEMU system emulator for Xtensa boards.

%package system-xtensa-core
Summary: QEMU system emulator for Xtensa
Requires: %{name}-common = %{epoch}:%{version}-%{release}
%description system-xtensa-core
This package provides the QEMU system emulator for Xtensa boards.




%prep
%setup -q -n qemu-%{version}%{?rcstr}
%autopatch -p1

# https://fedoraproject.org/wiki/Changes/Make_ambiguous_python_shebangs_error
# Fix all Python shebangs recursively in .
# -p preserves timestamps
# -n prevents creating ~backup files
# -i specifies the interpreter for the shebang
# Need to list files that do not match ^[a-zA-Z0-9_]+\.py$ explicitly!
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/qemu-trace-stap




%build

# drop -g flag to prevent memory exhaustion by linker
%ifarch s390
%global optflags %(echo %{optflags} | sed 's/-g//')
sed -i.debug 's/"-g $CFLAGS"/"$CFLAGS"/g' configure
%endif

# OOM killer breaks builds with parallel make on s390(x)
%ifarch s390 s390x
%global _smp_mflags %{nil}
%endif

# --build-id option is used for giving info to the debug packages.
extraldflags="-Wl,--build-id";
buildldflags="VL_LDFLAGS=-Wl,--build-id"

# As of qemu 2.1, --enable-trace-backends supports multiple backends,
# but there's a performance impact for non-dtrace so we don't use them
tracebackends="dtrace"

%if %{have_spice}
    %global spiceflag --enable-spice
%else
    %global spiceflag --disable-spice
%endif


run_configure() {
    # Base configure call with standard shared options
    ../configure \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir} \
        --localstatedir=%{_localstatedir} \
        --libexecdir=%{_libexecdir} \
        --interp-prefix=%{_prefix}/qemu-%%M \
        --with-pkgversion=%{name}-%{version}-%{release} \
        --extra-ldflags="$extraldflags -Wl,-z,relro -Wl,-z,now" \
        --extra-cflags="%{optflags}" \
        --python=%{__python3} \
        --disable-strip \
        --disable-werror \
        --tls-priority=@QEMU,SYSTEM \
        --enable-trace-backend=$tracebackends \
        "$@" || cat config.log
}

run_configure_disable_everything() {
    # Disable every qemu feature. Callers can --enable-X the bits they need
    run_configure \
        --audio-drv-list= \
        --disable-attr \
        --disable-auth-pam \
        --disable-avx2 \
        --disable-blobs \
        --disable-bluez \
        --disable-bochs \
        --disable-brlapi \
        --disable-bsd-user \
        --disable-bzip2 \
        --disable-cap-ng \
        --disable-capstone \
        --disable-cloop \
        --disable-cocoa \
        --disable-coroutine-pool \
        --disable-crypto-afalg \
        --disable-curl \
        --disable-curses \
        --disable-debug-info \
        --disable-debug-mutex \
        --disable-debug-tcg \
        --disable-dmg \
        --disable-docs \
        --disable-fdt \
        --disable-gcrypt \
        --disable-glusterfs \
        --disable-gnutls \
        --disable-gtk \
        --disable-guest-agent \
        --disable-guest-agent-msi \
        --disable-hax \
        --disable-hvf \
        --disable-iconv \
        --disable-jemalloc \
        --disable-kvm \
        --disable-libiscsi \
        --disable-libnfs \
        --disable-libpmem \
        --disable-libssh \
        --disable-libusb \
        --disable-libxml2 \
        --disable-linux-aio \
        --disable-linux-user \
        --disable-live-block-migration \
        --disable-lzfse \
        --disable-lzo \
        --disable-membarrier \
        --disable-modules \
        --disable-mpath \
        --disable-netmap \
        --disable-nettle \
        --disable-numa \
        --disable-opengl \
        --disable-parallels \
        --disable-pie \
        --disable-pvrdma \
        --disable-qcow1 \
        --disable-qed \
        --disable-qom-cast-debug \
        --disable-rbd \
        --disable-rdma \
        --disable-replication \
        --disable-sdl \
        --disable-sdl-image \
        --disable-seccomp \
        --disable-sheepdog \
        --disable-slirp \
        --disable-smartcard \
        --disable-snappy \
        --disable-sparse \
        --disable-spice \
        --disable-system \
        --disable-tcmalloc \
        --disable-tools \
        --disable-tpm \
        --disable-usb-redir \
        --disable-user \
        --disable-vde \
        --disable-vdi \
        --disable-vhost-crypto \
        --disable-vhost-kernel \
        --disable-vhost-net \
        --disable-vhost-scsi \
        --disable-vhost-user \
        --disable-vhost-vsock \
        --disable-virglrenderer \
        --disable-virtfs \
        --disable-vnc \
        --disable-vnc-jpeg \
        --disable-vnc-png \
        --disable-vnc-sasl \
        --disable-vte \
        --disable-vvfat \
        --disable-vxhs \
        --disable-whpx \
        --disable-xen \
        --disable-xen-pci-passthrough \
        --disable-xfsctl \
        --without-default-devices \
        "$@"
}



# Build for qemu-user-static
%if %{user_static}
mkdir build-static
pushd build-static

run_configure_disable_everything \
    --disable-pie \
    --enable-attr \
    --enable-linux-user \
    --static

make V=1 %{?_smp_mflags} $buildldflags

popd
%endif


# Build for qemu-mini
%if %{user_mini}
mkdir build-mini
pushd build-mini

run_configure_disable_everything                \
    --target-list="%{_arch}-softmmu"            \
    --enable-kvm                                \
    --enable-system                             \
    --enable-virtfs                             \
    --enable-cap-ng                             \
    --enable-attr                               \
    --enable-vhost-vsock                        \
    --enable-vhost-kernel                       \
    --enable-linux-aio                          \
    --enable-debug-info

make V=1 %{?_smp_mflags} $buildldflags

popd
%endif


# Build for non-static qemu-*
mkdir build-dynamic
pushd build-dynamic

run_configure \
    --audio-drv-list=pa,sdl,alsa,oss \
    --enable-kvm \
    --enable-system \
    --enable-linux-user \
    --enable-pie \
    --enable-modules \
    --enable-mpath \
    %{spiceflag} \
%ifarch s390 %{mips64}
    --enable-tcg-interpreter \
%endif
%if 0%{?fedora} > 30
    --enable-slirp=system \
%endif

echo "config-host.mak contents:"
echo "==="
cat config-host.mak
echo "==="

make V=1 %{?_smp_mflags} $buildldflags

popd




%install

%global _udevdir /lib/udev/rules.d
%global qemudocdir %{_docdir}/%{name}


# Install rules to use the bridge helper with libvirt's virbr0
install -D -m 0644 %{_sourcedir}/bridge.conf %{buildroot}%{_sysconfdir}/qemu/bridge.conf


# Install qemu-guest-agent service and udev rules
install -D -p -m 0644 %{_sourcedir}/qemu-guest-agent.service %{buildroot}%{_unitdir}/qemu-guest-agent.service
install -D -p -m 0644 %{_sourcedir}/qemu-ga.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/qemu-ga
install -D -m 0644 %{_sourcedir}/99-qemu-guest-agent.rules %{buildroot}%{_udevdir}/99-qemu-guest-agent.rules


# Install qemu-ga fsfreeze bits
mkdir -p %{buildroot}%{_sysconfdir}/qemu-ga/fsfreeze-hook.d
install -p -m 0755 scripts/qemu-guest-agent/fsfreeze-hook %{buildroot}%{_sysconfdir}/qemu-ga
install -p -m 0644 scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample %{buildroot}%{_sysconfdir}/qemu-ga/fsfreeze-hook.d/
mkdir -p %{buildroot}%{_localstatedir}/log
touch %{buildroot}%{_localstatedir}/log/qga-fsfreeze-hook.log


# Install qemu-pr-helper service
install -m 0644 %{_sourcedir}/qemu-pr-helper.service %{buildroot}%{_unitdir}
install -m 0644 %{_sourcedir}/qemu-pr-helper.socket %{buildroot}%{_unitdir}


# Install ppc64 memlock
%ifarch %{power64}
install -d %{buildroot}%{_sysconfdir}/security/limits.d
install -m 0644 %{_sourcedir}/95-kvm-ppc64-memlock.conf %{buildroot}%{_sysconfdir}/security/limits.d
%endif


# Install qemu-user-static tree
mkdir -p %{buildroot}%{_bindir}
%if %{user_static}
pushd build-static
make DESTDIR=%{buildroot} install

# Rename all QEMU user emulators to have a -static suffix
for src in %{buildroot}%{_bindir}/qemu-*
do
  mv $src $src-static
done

# Rename trace files to match -static suffix
for src in %{buildroot}%{_datadir}/systemtap/tapset/qemu-*.stp
do
  dst=`echo $src | sed -e 's/.stp/-static.stp/'`
  mv $src $dst
  perl -i -p -e 's/(qemu-\w+)/$1-static/g; s/(qemu\.user\.\w+)/$1.static/g' $dst
done

popd
%endif


# Install qemu-mini tree
%if %{user_mini}
pushd build-mini
install -D -p -m 0755 %{_arch}-softmmu/qemu-system-%{_arch} %{buildroot}/%{_bindir}/qemu-system-%{_arch}-mini

for src in %{_arch}-softmmu/qemu-*.stp; do
  dstbase=`basename $src | sed -e 's/.stp/-mini.stp/'`
  dst=%{buildroot}/%{_datadir}/systemtap/tapset/$dstbase
  install -D -p -m 0644 $src $dst
  perl -i -p -e 's/(qemu-\w+)/$1-mini/g; s/(qemu\.user\.\w*)/$1.mini/g' $dst
done
popd
%endif  # build_mini


# Install main qemu-system-* tree
pushd build-dynamic
make DESTDIR=%{buildroot} install
popd
%find_lang %{name}


# Copy some static data into place
install -D -p -m 0644 -t %{buildroot}%{qemudocdir} Changelog README COPYING COPYING.LIB LICENSE
install -D -p -m 0644 qemu.sasl %{buildroot}%{_sysconfdir}/sasl2/qemu.conf


# Generate qemu-system-* man pages
chmod -x %{buildroot}%{_mandir}/man1/*
for emu in %{buildroot}%{_bindir}/qemu-system-*; do
    ln -sf qemu.1.gz %{buildroot}%{_mandir}/man1/$(basename $emu).1.gz
done


# Install kvm specific source bits, and qemu-kvm manpage
%if 0%{?need_qemu_kvm}
ln -sf qemu.1.gz %{buildroot}%{_mandir}/man1/qemu-kvm.1.gz
install -m 0755 %{_sourcedir}/qemu-kvm.sh %{buildroot}%{_bindir}/qemu-kvm
install -D -p -m 0644 %{_sourcedir}/kvm-x86.modprobe.conf %{buildroot}%{_sysconfdir}/modprobe.d/kvm.conf
%endif

%if 0%{user_mini}
ln -sf qemu.1.gz %{buildroot}%{_mandir}/man1/qemu-mini.1.gz
ln -sf qemu-system-%{_arch}-mini %{buildroot}%{_bindir}/qemu-mini
%endif

# Install binfmt
%global binfmt_dir %{buildroot}%{_exec_prefix}/lib/binfmt.d
mkdir -p %{binfmt_dir}

./scripts/qemu-binfmt-conf.sh --systemd ALL --exportdir %{binfmt_dir} --qemu-path %{_bindir}
for i in %{binfmt_dir}/*; do
    mv $i $(echo $i | sed 's/.conf/-dynamic.conf/')
done

%if %{user_static}
for regularfmt in %{binfmt_dir}/*; do
  staticfmt="$(echo $regularfmt | sed 's/-dynamic/-static/g')"
  cat $regularfmt | tr -d '\n' | sed "s/:$/-static:F/" > $staticfmt
done
%endif


# XXX With qemu 2.11 we can probably drop this symlinking with use of
# configure --firmwarepath, see qemu git 3d5eecab4

# Provided by package openbios
rm -rf %{buildroot}%{_datadir}/%{name}/openbios-ppc
rm -rf %{buildroot}%{_datadir}/%{name}/openbios-sparc32
rm -rf %{buildroot}%{_datadir}/%{name}/openbios-sparc64
# Provided by package SLOF
rm -rf %{buildroot}%{_datadir}/%{name}/slof.bin
# Provided by package ipxe
rm -rf %{buildroot}%{_datadir}/%{name}/pxe*rom
rm -rf %{buildroot}%{_datadir}/%{name}/efi*rom
# Provided by package seavgabios
rm -rf %{buildroot}%{_datadir}/%{name}/vgabios*bin
# Provided by package seabios
rm -rf %{buildroot}%{_datadir}/%{name}/bios.bin
rm -rf %{buildroot}%{_datadir}/%{name}/bios-256k.bin
# Provided by package sgabios
rm -rf %{buildroot}%{_datadir}/%{name}/sgabios.bin
# Provided by package edk2
rm -rf %{buildroot}%{_datadir}/%{name}/edk2*
rm -rf %{buildroot}%{_datadir}/%{name}/firmware/*edk2*.json

pxe_link() {
  ln -s ../ipxe/$2.rom %{buildroot}%{_datadir}/%{name}/pxe-$1.rom
  ln -s ../ipxe.efi/$2.rom %{buildroot}%{_datadir}/%{name}/efi-$1.rom
}

pxe_link e1000 8086100e
pxe_link ne2k_pci 10ec8029
pxe_link pcnet 10222000
pxe_link rtl8139 10ec8139
pxe_link virtio 1af41000
pxe_link eepro100 80861209
pxe_link e1000e 808610d3
pxe_link vmxnet3 15ad07b0

rom_link() {
    ln -s $1 %{buildroot}%{_datadir}/%{name}/$2
}

rom_link ../seavgabios/vgabios-isavga.bin vgabios.bin
rom_link ../seavgabios/vgabios-cirrus.bin vgabios-cirrus.bin
rom_link ../seavgabios/vgabios-qxl.bin vgabios-qxl.bin
rom_link ../seavgabios/vgabios-stdvga.bin vgabios-stdvga.bin
rom_link ../seavgabios/vgabios-vmware.bin vgabios-vmware.bin
rom_link ../seavgabios/vgabios-virtio.bin vgabios-virtio.bin
rom_link ../seavgabios/vgabios-ramfb.bin vgabios-ramfb.bin
rom_link ../seavgabios/vgabios-bochs-display.bin vgabios-bochs-display.bin
rom_link ../seavgabios/vgabios-ati.bin vgabios-ati.bin
rom_link ../seabios/bios.bin bios.bin
rom_link ../seabios/bios-256k.bin bios-256k.bin
rom_link ../sgabios/sgabios.bin sgabios.bin


# When building using 'rpmbuild' or 'fedpkg local', RPATHs can be left in
# the binaries and libraries (although this doesn't occur when
# building in Koji, for some unknown reason). Some discussion here:
#
# https://lists.fedoraproject.org/pipermail/devel/2013-November/192553.html
#
# In any case it should always be safe to remove RPATHs from
# the final binaries:
for f in %{buildroot}%{_bindir}/* %{buildroot}%{_libdir}/* \
         %{buildroot}%{_libexecdir}/*; do
  if file $f | grep -q ELF | grep -q -i shared; then chrpath --delete $f; fi
done


# We need to make the modules executable else
# RPM won't pick up their dependencies.
chmod +x %{buildroot}%{_libdir}/qemu/*.so



%check
# Tests are hanging on s390 as of 2.3.0
#   https://bugzilla.redhat.com/show_bug.cgi?id=1206057
# Tests seem to be a recurring problem on s390, so I'd suggest just leaving
# it disabled.
%global archs_skip_tests s390
%global archs_ignore_test_failures 0

# Enable this temporarily if tests are broken
%global temp_skip_check 0

pushd build-dynamic
%ifnarch %{archs_skip_tests}

# Check the binary runs (see eg RHBZ#998722).
b="./x86_64-softmmu/qemu-system-x86_64"
if [ -x "$b" ]; then "$b" -help; fi

%ifarch %{archs_ignore_test_failures}
make check V=1 || :
%else
 %if %{temp_skip_check}
 make check V=1 || :
 %else
 make check V=1
 %endif
%endif

%if 0%{?hostqemu:1}
# Sanity-check current kernel can boot on this qemu.
# The results are advisory only.
qemu-sanity-check --qemu=%{?hostqemu} ||:
%endif

%endif
popd


%post common
getent group kvm >/dev/null || groupadd -g 36 -r kvm
getent group qemu >/dev/null || groupadd -g 107 -r qemu
getent passwd qemu >/dev/null || \
  useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
    -c "qemu user" qemu


%post user-binfmt
/bin/systemctl --system try-restart systemd-binfmt.service &>/dev/null || :
%postun user-binfmt
/bin/systemctl --system try-restart systemd-binfmt.service &>/dev/null || :

%if %{user_static}
%post user-static
/bin/systemctl --system try-restart systemd-binfmt.service &>/dev/null || :
%postun user-static
/bin/systemctl --system try-restart systemd-binfmt.service &>/dev/null || :
%endif

%post guest-agent
%systemd_post qemu-guest-agent.service
%preun guest-agent
%systemd_preun qemu-guest-agent.service
%postun guest-agent
%systemd_postun_with_restart qemu-guest-agent.service



%files
# Deliberately empty


%files common -f %{name}.lang
%dir %{qemudocdir}
%doc %{qemudocdir}/Changelog
%doc %{qemudocdir}/COPYING
%doc %{qemudocdir}/COPYING.LIB
%doc %{qemudocdir}/LICENSE
%doc %{qemudocdir}/qemu-doc.html
%doc %{qemudocdir}/qemu-doc.txt
%doc %{qemudocdir}/qemu-ga-ref.html
%doc %{qemudocdir}/qemu-ga-ref.txt
%doc %{qemudocdir}/qemu-qmp-ref.html
%doc %{qemudocdir}/qemu-qmp-ref.txt
%doc %{qemudocdir}/README
%doc %{qemudocdir}/interop
%doc %{qemudocdir}/specs
%dir %{_datadir}/%{name}/
%{_datadir}/applications/qemu.desktop
%{_datadir}/icons/hicolor/*/apps/*
%exclude %{_datadir}/%{name}/qemu-nsis.bmp
%{_datadir}/%{name}/keymaps/
%{_datadir}/%{name}/trace-events-all
%{_datadir}/%{name}/vgabios.bin
%{_datadir}/%{name}/vgabios-cirrus.bin
%{_datadir}/%{name}/vgabios-qxl.bin
%{_datadir}/%{name}/vgabios-stdvga.bin
%{_datadir}/%{name}/vgabios-vmware.bin
%{_datadir}/%{name}/vgabios-virtio.bin
%{_datadir}/%{name}/vgabios-ramfb.bin
%{_datadir}/%{name}/vgabios-bochs-display.bin
%{_datadir}/%{name}/vgabios-ati.bin
%{_datadir}/%{name}/pxe-e1000.rom
%{_datadir}/%{name}/efi-e1000.rom
%{_datadir}/%{name}/pxe-e1000e.rom
%{_datadir}/%{name}/efi-e1000e.rom
%{_datadir}/%{name}/pxe-eepro100.rom
%{_datadir}/%{name}/efi-eepro100.rom
%{_datadir}/%{name}/pxe-ne2k_pci.rom
%{_datadir}/%{name}/efi-ne2k_pci.rom
%{_datadir}/%{name}/pxe-pcnet.rom
%{_datadir}/%{name}/efi-pcnet.rom
%{_datadir}/%{name}/pxe-rtl8139.rom
%{_datadir}/%{name}/efi-rtl8139.rom
%{_datadir}/%{name}/pxe-virtio.rom
%{_datadir}/%{name}/efi-virtio.rom
%{_datadir}/%{name}/pxe-vmxnet3.rom
%{_datadir}/%{name}/efi-vmxnet3.rom
%{_datadir}/%{name}/vhost-user/50-qemu-gpu.json
%{_mandir}/man1/qemu.1*
%{_mandir}/man1/qemu-trace-stap.1*
%{_mandir}/man1/virtfs-proxy-helper.1*
%{_mandir}/man7/qemu-block-drivers.7*
%{_mandir}/man7/qemu-cpu-models.7*
%{_mandir}/man7/qemu-ga-ref.7*
%{_mandir}/man7/qemu-qmp-ref.7*
%{_bindir}/elf2dmp
%{_bindir}/qemu-edid
%{_bindir}/qemu-keymap
%{_bindir}/qemu-pr-helper
%{_bindir}/qemu-trace-stap
%{_bindir}/virtfs-proxy-helper
%{_unitdir}/qemu-pr-helper.service
%{_unitdir}/qemu-pr-helper.socket
%attr(4755, root, root) %{_libexecdir}/qemu-bridge-helper
%{_libexecdir}/vhost-user-gpu
%config(noreplace) %{_sysconfdir}/sasl2/qemu.conf
%dir %{_sysconfdir}/qemu
%config(noreplace) %{_sysconfdir}/qemu/bridge.conf
%dir %{_libdir}/qemu


%files guest-agent
%{_bindir}/qemu-ga
%{_mandir}/man8/qemu-ga.8*
%{_unitdir}/qemu-guest-agent.service
%{_udevdir}/99-qemu-guest-agent.rules
%config(noreplace) %{_sysconfdir}/sysconfig/qemu-ga
%{_sysconfdir}/qemu-ga
%ghost %{_localstatedir}/log/qga-fsfreeze-hook.log


%files img
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man8/qemu-nbd.8*


%files block-curl
%{_libdir}/qemu/block-curl.so
%files block-dmg
%{_libdir}/qemu/block-dmg-bz2.so
%if %{with_block_gluster}
%files block-gluster
%{_libdir}/qemu/block-gluster.so
%endif
%files block-iscsi
%{_libdir}/qemu/block-iscsi.so
%files block-nfs
%{_libdir}/qemu/block-nfs.so
%if %{with_block_rbd}
%files block-rbd
%{_libdir}/qemu/block-rbd.so
%endif
%files block-ssh
%{_libdir}/qemu/block-ssh.so


%files audio-alsa
%{_libdir}/qemu/audio-alsa.so
%files audio-oss
%{_libdir}/qemu/audio-oss.so
%files audio-pa
%{_libdir}/qemu/audio-pa.so
%files audio-sdl
%{_libdir}/qemu/audio-sdl.so


%files ui-curses
%{_libdir}/qemu/ui-curses.so
%files ui-gtk
%{_libdir}/qemu/ui-gtk.so
%files ui-sdl
%{_libdir}/qemu/ui-sdl.so


%files -n ivshmem-tools
%{_bindir}/ivshmem-client
%{_bindir}/ivshmem-server


%if %{have_kvm}
%files kvm
# Deliberately empty

%files kvm-core
# Deliberately empty
%endif

%if %{user_mini}
%files mini
%{_bindir}/qemu-mini
%{_mandir}/man1/qemu-mini.1.gz
%{_mandir}/man1/qemu-system-%{_arch}-mini.1.gz
%endif

%files user
%{_bindir}/qemu-i386
%{_bindir}/qemu-x86_64
%{_bindir}/qemu-aarch64
%{_bindir}/qemu-aarch64_be
%{_bindir}/qemu-alpha
%{_bindir}/qemu-arm
%{_bindir}/qemu-armeb
%{_bindir}/qemu-cris
%{_bindir}/qemu-hppa
%{_bindir}/qemu-m68k
%{_bindir}/qemu-microblaze
%{_bindir}/qemu-microblazeel
%{_bindir}/qemu-mips
%{_bindir}/qemu-mipsel
%{_bindir}/qemu-mips64
%{_bindir}/qemu-mips64el
%{_bindir}/qemu-mipsn32
%{_bindir}/qemu-mipsn32el
%{_bindir}/qemu-nios2
%{_bindir}/qemu-or1k
%{_bindir}/qemu-ppc
%{_bindir}/qemu-ppc64
%{_bindir}/qemu-ppc64abi32
%{_bindir}/qemu-ppc64le
%{_bindir}/qemu-riscv32
%{_bindir}/qemu-riscv64
%{_bindir}/qemu-s390x
%{_bindir}/qemu-sh4
%{_bindir}/qemu-sh4eb
%{_bindir}/qemu-sparc
%{_bindir}/qemu-sparc32plus
%{_bindir}/qemu-sparc64
%{_bindir}/qemu-tilegx
%{_bindir}/qemu-xtensa
%{_bindir}/qemu-xtensaeb

%{_datadir}/systemtap/tapset/qemu-i386.stp
%{_datadir}/systemtap/tapset/qemu-i386-log.stp
%{_datadir}/systemtap/tapset/qemu-i386-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-x86_64.stp
%{_datadir}/systemtap/tapset/qemu-x86_64-log.stp
%{_datadir}/systemtap/tapset/qemu-x86_64-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-aarch64.stp
%{_datadir}/systemtap/tapset/qemu-aarch64-log.stp
%{_datadir}/systemtap/tapset/qemu-aarch64-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-aarch64_be.stp
%{_datadir}/systemtap/tapset/qemu-aarch64_be-log.stp
%{_datadir}/systemtap/tapset/qemu-aarch64_be-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-alpha.stp
%{_datadir}/systemtap/tapset/qemu-alpha-log.stp
%{_datadir}/systemtap/tapset/qemu-alpha-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-arm.stp
%{_datadir}/systemtap/tapset/qemu-arm-log.stp
%{_datadir}/systemtap/tapset/qemu-arm-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-armeb.stp
%{_datadir}/systemtap/tapset/qemu-armeb-log.stp
%{_datadir}/systemtap/tapset/qemu-armeb-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-cris.stp
%{_datadir}/systemtap/tapset/qemu-cris-log.stp
%{_datadir}/systemtap/tapset/qemu-cris-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-hppa.stp
%{_datadir}/systemtap/tapset/qemu-hppa-log.stp
%{_datadir}/systemtap/tapset/qemu-hppa-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-m68k.stp
%{_datadir}/systemtap/tapset/qemu-m68k-log.stp
%{_datadir}/systemtap/tapset/qemu-m68k-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-microblaze.stp
%{_datadir}/systemtap/tapset/qemu-microblaze-log.stp
%{_datadir}/systemtap/tapset/qemu-microblaze-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-microblazeel.stp
%{_datadir}/systemtap/tapset/qemu-microblazeel-log.stp
%{_datadir}/systemtap/tapset/qemu-microblazeel-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-mips.stp
%{_datadir}/systemtap/tapset/qemu-mips-log.stp
%{_datadir}/systemtap/tapset/qemu-mips-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-mipsel.stp
%{_datadir}/systemtap/tapset/qemu-mipsel-log.stp
%{_datadir}/systemtap/tapset/qemu-mipsel-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-mips64.stp
%{_datadir}/systemtap/tapset/qemu-mips64-log.stp
%{_datadir}/systemtap/tapset/qemu-mips64-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-mips64el.stp
%{_datadir}/systemtap/tapset/qemu-mips64el-log.stp
%{_datadir}/systemtap/tapset/qemu-mips64el-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-mipsn32.stp
%{_datadir}/systemtap/tapset/qemu-mipsn32-log.stp
%{_datadir}/systemtap/tapset/qemu-mipsn32-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-mipsn32el.stp
%{_datadir}/systemtap/tapset/qemu-mipsn32el-log.stp
%{_datadir}/systemtap/tapset/qemu-mipsn32el-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-nios2.stp
%{_datadir}/systemtap/tapset/qemu-nios2-log.stp
%{_datadir}/systemtap/tapset/qemu-nios2-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-or1k.stp
%{_datadir}/systemtap/tapset/qemu-or1k-log.stp
%{_datadir}/systemtap/tapset/qemu-or1k-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-ppc.stp
%{_datadir}/systemtap/tapset/qemu-ppc-log.stp
%{_datadir}/systemtap/tapset/qemu-ppc-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-ppc64.stp
%{_datadir}/systemtap/tapset/qemu-ppc64-log.stp
%{_datadir}/systemtap/tapset/qemu-ppc64-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-ppc64abi32.stp
%{_datadir}/systemtap/tapset/qemu-ppc64abi32-log.stp
%{_datadir}/systemtap/tapset/qemu-ppc64abi32-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-ppc64le.stp
%{_datadir}/systemtap/tapset/qemu-ppc64le-log.stp
%{_datadir}/systemtap/tapset/qemu-ppc64le-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-riscv32.stp
%{_datadir}/systemtap/tapset/qemu-riscv32-log.stp
%{_datadir}/systemtap/tapset/qemu-riscv32-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-riscv64.stp
%{_datadir}/systemtap/tapset/qemu-riscv64-log.stp
%{_datadir}/systemtap/tapset/qemu-riscv64-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-s390x.stp
%{_datadir}/systemtap/tapset/qemu-s390x-log.stp
%{_datadir}/systemtap/tapset/qemu-s390x-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-sh4.stp
%{_datadir}/systemtap/tapset/qemu-sh4-log.stp
%{_datadir}/systemtap/tapset/qemu-sh4-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-sh4eb.stp
%{_datadir}/systemtap/tapset/qemu-sh4eb-log.stp
%{_datadir}/systemtap/tapset/qemu-sh4eb-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-sparc.stp
%{_datadir}/systemtap/tapset/qemu-sparc-log.stp
%{_datadir}/systemtap/tapset/qemu-sparc-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-sparc32plus.stp
%{_datadir}/systemtap/tapset/qemu-sparc32plus-log.stp
%{_datadir}/systemtap/tapset/qemu-sparc32plus-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-sparc64.stp
%{_datadir}/systemtap/tapset/qemu-sparc64-log.stp
%{_datadir}/systemtap/tapset/qemu-sparc64-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-tilegx.stp
%{_datadir}/systemtap/tapset/qemu-tilegx-log.stp
%{_datadir}/systemtap/tapset/qemu-tilegx-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-xtensa.stp
%{_datadir}/systemtap/tapset/qemu-xtensa-log.stp
%{_datadir}/systemtap/tapset/qemu-xtensa-simpletrace.stp
%{_datadir}/systemtap/tapset/qemu-xtensaeb.stp
%{_datadir}/systemtap/tapset/qemu-xtensaeb-log.stp
%{_datadir}/systemtap/tapset/qemu-xtensaeb-simpletrace.stp

%files user-binfmt
%{_exec_prefix}/lib/binfmt.d/qemu-*-dynamic.conf

%if %{user_static}
%files user-static
# Just use wildcard matches here: we will catch any new/missing files
# in the qemu-user filelists
%{_exec_prefix}/lib/binfmt.d/qemu-*-static.conf
%{_bindir}/qemu-*-static
%{_datadir}/systemtap/tapset/qemu-*-static.stp
%endif


%files system-aarch64
%files system-aarch64-core
%{_bindir}/qemu-system-aarch64
%{_datadir}/systemtap/tapset/qemu-system-aarch64*.stp
%{_mandir}/man1/qemu-system-aarch64.1*
%ifarch aarch64
%files system-aarch64-mini
%{_bindir}/qemu-system-aarch64-mini
%{_datadir}/systemtap/tapset/qemu-system-aarch64*-mini.stp
%endif


%files system-alpha
%files system-alpha-core
%{_bindir}/qemu-system-alpha
%{_datadir}/systemtap/tapset/qemu-system-alpha*.stp
%{_mandir}/man1/qemu-system-alpha.1*
%{_datadir}/%{name}/palcode-clipper


%files system-arm
%files system-arm-core
%{_bindir}/qemu-system-arm
%{_datadir}/systemtap/tapset/qemu-system-arm*.stp
%{_mandir}/man1/qemu-system-arm.1*
%ifarch %{arm}
%files system-arm-mini
%{_bindir}/qemu-system-arm-mini
%{_datadir}/systemtap/tapset/qemu-system-arm*-mini.stp
%endif

%files system-cris
%files system-cris-core
%{_bindir}/qemu-system-cris
%{_datadir}/systemtap/tapset/qemu-system-cris*.stp
%{_mandir}/man1/qemu-system-cris.1*


%files system-hppa
%files system-hppa-core
%{_bindir}/qemu-system-hppa
%{_datadir}/systemtap/tapset/qemu-system-hppa*.stp
%{_mandir}/man1/qemu-system-hppa.1*
%{_datadir}/%{name}/hppa-firmware.img


%files system-lm32
%files system-lm32-core
%{_bindir}/qemu-system-lm32
%{_datadir}/systemtap/tapset/qemu-system-lm32*.stp
%{_mandir}/man1/qemu-system-lm32.1*


%files system-m68k
%files system-m68k-core
%{_bindir}/qemu-system-m68k
%{_datadir}/systemtap/tapset/qemu-system-m68k*.stp
%{_mandir}/man1/qemu-system-m68k.1*


%files system-microblaze
%files system-microblaze-core
%{_bindir}/qemu-system-microblaze
%{_bindir}/qemu-system-microblazeel
%{_datadir}/systemtap/tapset/qemu-system-microblaze*.stp
%{_mandir}/man1/qemu-system-microblaze.1*
%{_mandir}/man1/qemu-system-microblazeel.1*
%{_datadir}/%{name}/petalogix*.dtb


%files system-mips
%files system-mips-core
%{_bindir}/qemu-system-mips
%{_bindir}/qemu-system-mipsel
%{_bindir}/qemu-system-mips64
%{_bindir}/qemu-system-mips64el
%{_datadir}/systemtap/tapset/qemu-system-mips*.stp
%{_mandir}/man1/qemu-system-mips.1*
%{_mandir}/man1/qemu-system-mipsel.1*
%{_mandir}/man1/qemu-system-mips64el.1*
%{_mandir}/man1/qemu-system-mips64.1*


%files system-moxie
%files system-moxie-core
%{_bindir}/qemu-system-moxie
%{_datadir}/systemtap/tapset/qemu-system-moxie*.stp
%{_mandir}/man1/qemu-system-moxie.1*


%files system-nios2
%files system-nios2-core
%{_bindir}/qemu-system-nios2
%{_datadir}/systemtap/tapset/qemu-system-nios2*.stp
%{_mandir}/man1/qemu-system-nios2.1*


%files system-or1k
%files system-or1k-core
%{_bindir}/qemu-system-or1k
%{_datadir}/systemtap/tapset/qemu-system-or1k*.stp
%{_mandir}/man1/qemu-system-or1k.1*


%files system-ppc
%files system-ppc-core
%{_bindir}/qemu-system-ppc
%{_bindir}/qemu-system-ppc64
%{_datadir}/systemtap/tapset/qemu-system-ppc*.stp
%{_mandir}/man1/qemu-system-ppc.1*
%{_mandir}/man1/qemu-system-ppc64.1*
%{_datadir}/%{name}/bamboo.dtb
%{_datadir}/%{name}/canyonlands.dtb
%{_datadir}/%{name}/ppc_rom.bin
%{_datadir}/%{name}/qemu_vga.ndrv
%{_datadir}/%{name}/skiboot.lid
%{_datadir}/%{name}/spapr-rtas.bin
%{_datadir}/%{name}/u-boot.e500
%{_datadir}/%{name}/u-boot-sam460-20100605.bin
%ifarch %{power64}
%{_sysconfdir}/security/limits.d/95-kvm-ppc64-memlock.conf
%endif
%ifarch %{power64}
%files system-ppc-mini
%{_bindir}/qemu-system-ppc-mini
%{_datadir}/systemtap/tapset/qemu-system-ppc*-mini.stp
%endif


%files system-riscv
%files system-riscv-core
%{_bindir}/qemu-system-riscv32
%{_bindir}/qemu-system-riscv64
%{_datadir}/%{name}/opensbi-riscv*.bin
%{_datadir}/systemtap/tapset/qemu-system-riscv*.stp
%{_mandir}/man1/qemu-system-riscv*.1*


%files system-s390x
%files system-s390x-core
%{_bindir}/qemu-system-s390x
%{_datadir}/systemtap/tapset/qemu-system-s390x*.stp
%{_mandir}/man1/qemu-system-s390x.1*
%{_datadir}/%{name}/s390-ccw.img
%{_datadir}/%{name}/s390-netboot.img
%ifarch s390x
%files system-s390x-mini
%{_bindir}/qemu-system-s390x-mini
%endif


%files system-sh4
%files system-sh4-core
%{_bindir}/qemu-system-sh4
%{_bindir}/qemu-system-sh4eb
%{_datadir}/systemtap/tapset/qemu-system-sh4*.stp
%{_mandir}/man1/qemu-system-sh4.1*
%{_mandir}/man1/qemu-system-sh4eb.1*


%files system-sparc
%files system-sparc-core
%{_bindir}/qemu-system-sparc
%{_bindir}/qemu-system-sparc64
%{_datadir}/systemtap/tapset/qemu-system-sparc*.stp
%{_mandir}/man1/qemu-system-sparc.1*
%{_mandir}/man1/qemu-system-sparc64.1*
%{_datadir}/%{name}/QEMU,tcx.bin
%{_datadir}/%{name}/QEMU,cgthree.bin


%files system-tricore
%files system-tricore-core
%{_bindir}/qemu-system-tricore
%{_datadir}/systemtap/tapset/qemu-system-tricore*.stp
%{_mandir}/man1/qemu-system-tricore.1*


%files system-unicore32
%files system-unicore32-core
%{_bindir}/qemu-system-unicore32
%{_datadir}/systemtap/tapset/qemu-system-unicore32*.stp
%{_mandir}/man1/qemu-system-unicore32.1*


%files system-x86
%files system-x86-core
%{_bindir}/qemu-system-i386
%{_bindir}/qemu-system-x86_64
%{_datadir}/systemtap/tapset/qemu-system-i386*.stp
%{_datadir}/systemtap/tapset/qemu-system-x86_64*.stp
%{_mandir}/man1/qemu-system-i386.1*
%{_mandir}/man1/qemu-system-x86_64.1*
%{_datadir}/%{name}/bios.bin
%{_datadir}/%{name}/bios-256k.bin
%{_datadir}/%{name}/kvmvapic.bin
%{_datadir}/%{name}/linuxboot.bin
%{_datadir}/%{name}/linuxboot_dma.bin
%{_datadir}/%{name}/multiboot.bin
%{_datadir}/%{name}/pvh.bin
%{_datadir}/%{name}/sgabios.bin
%if 0%{?need_qemu_kvm}
%{_bindir}/qemu-kvm
%{_mandir}/man1/qemu-kvm.1*
%config(noreplace) %{_sysconfdir}/modprobe.d/kvm.conf
%endif
%ifarch x86_64
%files system-x86-mini
%{_bindir}/qemu-system-x86_64-mini
%{_datadir}/systemtap/tapset/qemu-system-x86_64*-mini.stp
%endif

%files system-xtensa
%files system-xtensa-core
%{_bindir}/qemu-system-xtensa
%{_bindir}/qemu-system-xtensaeb
%{_datadir}/systemtap/tapset/qemu-system-xtensa*.stp
%{_mandir}/man1/qemu-system-xtensa.1*
%{_mandir}/man1/qemu-system-xtensaeb.1*


%changelog
* Mon Sep 2 2019 Christophe de Dinechin <dinechin@redhat.com> - 2:4.1.0-1.2
- Add qemu-mini experimental build

* Mon Aug 19 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.1.0-1
- Update to qemu-4.1.0 GA

* Wed Jul 17 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.1.0-0.1.rc2
- Update to qemu-4.1.0-rc2
- Re-add libattr for qemu-user-static (bz 1731756)

* Wed Jul 17 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.1.0-0.1.rc1
- Update to qemu-4.1.0-rc1

* Thu Jul 11 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.1.0-0.1.rc0
- Update to qemu-4.1.0-rc0

* Fri Jun 28 2019 Kevin Fenzi <kevin@scrye.com> - 2:4.0.0-5
- Rebuild for new brltty.

* Thu Jun 20 2019 Cole Robinson <crobinso@redhat.com> - 2:4.0.0-4
- CVE-2019-12155: qxl: null pointer dereference while releasing spice
  resources (bz #1712727, bz #1712670)
- qemu-4.0.0-2.fc31 ppc64le: rpm hash calculation buggy (bz #1715017)
- Fix rawhide build (bz #1718926)
- Link against libslirp (bz #1712980)
- Add vgabios-ramfb.bin and vgabios-bochs-display.bin (bz #1721445)

* Tue May 14 2019 Daniel P. Berrangé <berrange@redhat.com> - 2:4.0.0-2
- Define md-clear CPUID bit
- Resolves: rhbz #1710002 (CVE-2018-12126), rhbz #1710004 (CVE-2018-12127),
  rhbz #1710003 (CVE-2018-12130), rhbz #1710006 (CVE-2019-11091)

* Wed Apr 24 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.0.0-1
- Update to qemu-4.0.0 GA

* Tue Apr 16 2019 Cole Robinson <crobinso@redhat.com> - 2:4.0.0-0.7.rc3
- Don't block migration with nested VMX (bz #1697997)
- Update to qemu-4.0.0-rc3

* Sat Apr 06 2019 Richard W.M. Jones <rjones@redhat.com> - 2:4.0.0-0.6.rc2
- Rebuild against xen 4.12.

* Wed Apr 03 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.0.0-0.5.rc2
- Update to 4.0.0-rc2

* Wed Mar 27 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.0.0-0.4.rc1
- Update to 4.0.0-rc1

* Mon Mar 25 2019 Adam Williamson <awilliam@redhat.com> - 2:4.0.0-0.3.rc0
- Backport patch to fix 3D crasher bug (bz #1692323)

* Thu Mar 21 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.0.0-0.2.rc0
- Fix python paths for qemu-trace-stap

* Wed Mar 20 2019 Cole Robinson <aintdiscole@gmail.com> - 2:4.0.0-0.2.rc0
- Update to 4.0.0-rc0

* Wed Mar 20 2019 Daniel P. Berrangé <berrange@redhat.com> - 2:3.1.0-5
- Fix compat with latest glibc which has gettid func

* Sun Mar 03 2019 Cole Robinson <aintdiscole@gmail.com> - 2:3.1.0-4.3
- Temporarily disable glusterfs (bz #1684298)

* Thu Feb 28 2019 Cole Robinson <aintdiscole@gmail.com> - 2:3.1.0-4.2
- Rebuild for brltty soname bump

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:3.1.0-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Jan 12 2019 Richard W.M. Jones <rjones@redhat.com> - 2:3.1.0-4
- Remove temporary patch and rebuild against fixed capstone.

* Fri Jan 11 2019 Richard W.M. Jones <rjones@redhat.com> - 2:3.1.0-3
- Rebuild for unannounced libcapstone soname bump from 3 to 4.
- Add a temporary patch to fix capstone header location.

* Tue Dec 18 2018 Adam Williamson <awilliam@redhat.com> - 2:3.1.0-1.1
- Restore patch to drop phantom 86 key from en-us keymap (bz #1658676)

* Tue Dec 11 2018 Cole Robinson <crobinso@redhat.com> - 2:3.1.0-1
- Rebase to qemu-3.1.0 GA

* Mon Dec 10 2018 Daniel P. Berrangé <berrange@redhat.com> - 2:3.1.0-0.2.rc1
- Disable RBD on 32-bit arches

* Thu Nov 15 2018 Cole Robinson <crobinso@redhat.com> - 2:3.1.0-0.1.rc1
- Rebase to qemu-3.1.0-rc1

* Wed Aug 15 2018 Cole Robinson <crobinso@redhat.com> - 2:3.0.0-1
- Rebase to qemu-3.0.0 GA

* Mon Aug 13 2018 Cole Robinson <crobinso@redhat.com> - 2:3.0.0-0.2.rc3
- Drop ksm package, moved to ksmtuned srpm

* Tue Jul 31 2018 Cole Robinson <crobinso@redhat.com> - 2:3.0.0-0.1.rc3
- Rebase to qemu-3.0.0-rc3
- Drop now unneeded s390x conf (bz #1609706)
- Only install modprobe kvm.conf on x86 (bz #1517989)

* Fri Jul 13 2018 Peter Robinson <pbrobinson@fedoraproject.org> 2:2.12.0-4
- Rebuild for Xen 4.11

* Mon Jun 18 2018 Daniel P. Berrangé <berrange@redhat.com> - 2:2.12.0-3
- New CPU features for speculative store bypass (CVE-2018-3639)

* Tue Jun 05 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-2
- Fix qxl memslot_get_virt crashes (bz #1565354)

* Mon Apr 30 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-1
- Update to qemu-2.12.0 GA

* Mon Apr 16 2018 Richard W.M. Jones <rjones@redhat.com> - 2:2.12.0-0.7.rc3
- Update to qemu-2.12.0-rc3
- Remove upstream patch.
- Fixes issues with partition / LV minimum alignment (RHBZ#1565714).

* Thu Apr 05 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-0.6.rc2
- Update to qemu-2.12.0-rc2

* Wed Mar 28 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-0.5.rc1
- Update to qemu-2.12.0-rc1

* Mon Mar 26 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-0.4.rc0
- Enable missing tilegx, xtensa* qemu-user targets

* Sun Mar 25 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-0.3.rc0
- Generate binfmt configs with qemu-binfmt-conf.sh

* Fri Mar 23 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-0.2.rc0
- Fix audio and ui module RPM deps
- Drop some arch restrictions for rdma, spice, xen, numactl
- Fix hppa firmware packaging

* Thu Mar 22 2018 Cole Robinson <crobinso@redhat.com> - 2:2.12.0-0.1.rc0
- Rebase to qemu-2.12.0-rc0
- Add hppa and riscv32/64 targets
- Add audio and ui modules

* Mon Mar 19 2018 Daniel P. Berrangé <berrange@redhat.com> - 2:2.11.1-2
- Re-enable normal hardened build macros to fix ksmctl.c hardening
- Don't strip _FORTIFY_SOURCE from compiler flags
- Don't pass -pie as an extra ldflags when we use --enable-pie

* Wed Feb 28 2018 Cole Robinson <crobinso@redhat.com> - 2:2.11.1-1
- Rebase to qemu 2.11.1 bugfix release

* Tue Feb 27 2018 Daniel P. Berrange <berrange@redhat.com> - 2:2.11.0-5
- Improve License tag
- Honour CC/LD flags for ksmctl
- Fix non-deterministic test failure
- Use explicit "python2" binary to avoid "python" brokeness (rhbz#1550010)
- Avoid breakage in TLS tests due to stricter crypto policies

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.11.0-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Dec 21 2017 Daniel P. Berrange <berrange@redhat.com> - 2:2.11.0-4
- Re-enable RBD on arm/ppc (rhbz #1528378)

* Wed Dec 20 2017 Adam Williamson <awilliam@redhat.com> - 2:2.11.0-3
- Fix problem with typing some characters via VNC (LP#1738283)

* Wed Dec 20 2017 Cole Robinson <crobinso@redhat.com> - 2:2.11.0-2
- Rebuild for xen 4.10

* Mon Dec 18 2017 Cole Robinson <crobinso@redhat.com> - 2:2.11.0-1
- Rebase to 2.11.0 GA

* Mon Dec 04 2017 Cole Robinson <crobinso@redhat.com> - 2:2.11.0-0.3-rc3
- Rebase to 2.11.0-rc3

* Tue Nov 28 2017 Paolo Bonzini <pbonzini@redhat.com> - 2:2.11.0-0.2.rc2
- Fix compilation
- Upgrade qemu-ga packaging based on RHEL 7

* Mon Nov 20 2017 Cole Robinson <crobinso@redhat.com> - 2:2.11.0-0.1.rc1
- Rebase to 2.11.0-rc1

* Thu Oct 19 2017 Cole Robinson <crobinso@redhat.com> - 2:2.10.1-1
- Fix ppc64 KVM failure (bz #1501936)
- CVE-2017-15038: 9p: information disclosure when reading extended
  attributes (bz #1499111)
- CVE-2017-15268: potential memory exhaustion via websock connection to VNC
  (bz #1496882)

* Tue Oct 17 2017 Paolo Bonzini <pbonzini@redhat.com> - 2:2.10.0-7
- Update patch 1014 for new libmultipath/libmpathpersist API
- Force build to fail if multipath is not available
- Tighten permissions on the qemu-pr-helper socket

* Mon Oct  9 2017 Daniel P. Berrange <berrange@redhat.com> - 2:2.10.0-6
- Rebuild for libiscsi changed soname again

* Tue Oct 03 2017 Paolo Bonzini <pbonzini@redhat.com> - 2:2.10.0-5
- Rebuild with new libiscsi for iSER support

* Thu Sep 28 2017 Paolo Bonzini <pbonzini@redhat.com> - 2:2.10.0-4
- Stop using tcmalloc, glibc got faster

* Fri Sep 22 2017 Paolo Bonzini <pbonzini@redhat.com> - 2:2.10.0-3
- Backport persistent reservation manager in preparation for SELinux work
- Fix previous patch

* Mon Sep 18 2017 Nathaniel McCallum <npmccallum@redhat.com> - 2:2.10.0-2
- Fix endianness of e_type in the ppc64le binfmt

* Thu Sep 07 2017 Cole Robinson <crobinso@redhat.com> - 2:2.10.0-1
- Rebase to 2.10.0 GA

* Tue Aug 29 2017 Nathaniel McCallum <npmccallum@redhat.com> - 2:2.10.0-0.5.rc4
- Fix incorrect byte order in e_machine field in ppc64le binfmt (#1486379)

* Fri Aug 25 2017 Cole Robinson <crobinso@redhat.com> - 2:2.10.0-0.4.rc4
- Rebase to 2.10.0-rc4

* Tue Aug 22 2017 Adam Williamson <awilliam@redhat.com> - 2:2.10.0-0.3.rc3
- Don't build against rdma on 32-bit ARM (#1484155)

* Wed Aug 16 2017 Cole Robinson <crobinso@redhat.com> - 2:2.10.0-0.2.rc3
- Rebase to 2.10.0-rc3

* Thu Aug 03 2017 Cole Robinson <crobinso@redhat.com> - 2:2.10.0-0.1.rc1
- Rebase to 2.10.0-rc1

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 2:2.9.0-9
- Rebuild with binutils fix for ppc64le (#1475636)

* Tue Jul 25 2017 Daniel Berrange <berrange@redhat.com> - 2:2.9.0-8
- Disabled RBD on arm & ppc64 (rhbz #1474743)

* Thu Jul 20 2017 Nathaniel McCallum <npmccallum@redhat.com> - 2:2.9.0-7
- Fix binfmt dependencies and post scriptlets
- Add binfmt for ppc64le

* Wed Jul 19 2017 Daniel Berrange <berrange@redhat.com> - 2:2.9.0-6
- Fixes for compat with Xen 4.9

* Tue Jul 18 2017 Nathaniel McCallum <npmccallum@redhat.com> - 2:2.9.0-5
- Fix ucontext_t references

* Tue Jul 18 2017 Daniel P. Berrange <berrange@redhat.com> - 2:2.9.0-4
- Rebuild for changed Xen sonames

* Wed Jul 12 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-3
- CVE-2017-8112: vmw_pvscsi: infinite loop in pvscsi_log2 (bz #1445622)
- CVE-2017-8309: audio: host memory lekage via capture buffer (bz #1446520)
- CVE-2017-8379: input: host memory lekage via keyboard events (bz #1446560)
- CVE-2017-8380: scsi: megasas: out-of-bounds read in megasas_mmio_write (bz
  #1446578)
- CVE-2017-7493: 9pfs: guest privilege escalation in virtfs mapped-file mode
  (bz #1451711)
- CVE-2017-9503: megasas: null pointer dereference while processing megasas
  command (bz #1459478)
- CVE-2017-10806: usb-redirect: stack buffer overflow in debug logging (bz
  #1468497)
- CVE-2017-9524: nbd: segfault due to client non-negotiation (bz #1460172)
- CVE-2017-10664: qemu-nbd: server breaks with SIGPIPE upon client abort (bz
  #1466192)

* Mon May 22 2017 Richard W.M. Jones <rjones@redhat.com> - 2:2.9.0-2
- Bump release and rebuild to try to fix _ZdlPvm symbol (see RHBZ#1452813).

* Tue Apr 25 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-1
- Rebase to qemu-2.9.0 GA

* Thu Apr 13 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-0.2-rc4
- Rebase to qemu-2.9.0-rc4
- Fix ipxe rom links for aarch64

* Sat Apr 08 2017 Richard W.M. Jones <rjones@redhat.com> - 2:2.9.0-0.2-rc3
- Backport upstream fix for assertion when copy-on-read=true (RHBZ#1439922).

* Tue Apr 04 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-0.1-rc3
- Rebase to qemu-2.9.0-rc3

* Wed Mar 29 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-0.1-rc2
- Rebase to qemu-2.9.0-rc2
- Add Obsoletes for or32-or1k rename (bz 1435016)
- spec: Pull in vga and pxe roms for ppc64 (bz 1431403)

* Tue Mar 21 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-0.1-rc1
- Rebase to qemu-2.9.0-rc1

* Wed Mar 15 2017 Cole Robinson <crobinso@redhat.com> - 2:2.9.0-0.1-rc0
* Rebase to qemu-2.9.0-rc0

* Mon Feb 20 2017 Daniel Berrange <berrange@redhat.com> - 2:2.8.0-2
- Drop texi2html BR, since QEMU switched to using makeinfo back in 2010

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.8.0-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild
