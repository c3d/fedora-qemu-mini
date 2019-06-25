Copy of [fedora qemu dist git](https://src.fedoraproject.org/rpms/qemu),
with changes on top to generate a stripped down qemu-mini-system-x86_64,
in a qemu-mini-x86 subpackage. Non-x86 package building is disabled,
for quick build turnaround and testing.

* `grep` the spec for build-mini, you'll find the ./configure line used
  to build qemu
* [mini-i386-softmmu.mak](mini-i386-softmmu.mak) is the build config
  we drop into qemu default-configs/i386-softmmu.mak for building
  the mini binary
* You can build a local RPM with: `fedpkg --name qemu --release master local`
