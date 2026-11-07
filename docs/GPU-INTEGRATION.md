# Xenos GPU integration

## Upstream source of truth

This repository links the complete [arelyx/xenos-linux-gpu](https://github.com/arelyx/xenos-linux-gpu) via Git submodule. It contains:

| Layer | Upstream location | Purpose |
|---|---|---|
| Kernel DRM | `kernel/xegpu/` | Xenos CP/ring/fences, display and DRM interface |
| GPU UAPI | `kernel/include/xegpu_uapi.h` | Driver interfaces |
| Hardware fixes | `kernel/patches/` | Xenon Linux 6.18 bring-up changes |
| Early GPU state | `userspace/` | EDRAM training and xegpu diagnostics |
| OpenGL | `mesa/patches/` | Freedreno a2xx Xenos variant |
| X server | `xorg/` | Big-endian Xorg/glamor integration |
| Session configuration | `config/` | Xorg and IceWM service examples |
| Results | `conformance/` | dEQP/Piglit test logs and tools |

## Documented results — NOT reproduced by X360Linux

The upstream README (October 2026) reports a modded Trinity Slim running Linux 6.18.58, Debian unstable ppc64 via NFS, OpenGL ES 2.0 and desktop OpenGL 2.0 on Xenos, an accelerated Xorg session and IceWM.

Its reported dEQP GLES2 pass rate is 17,063 out of 17,075 executed test cases. This is **not** a statement of 100% OpenGL conformance, cross-board support or verification by this repository.

## Recommended integration sequence

1. Validate the matching **Free60 6.18 Xenon** kernel patch and known-good XeLL loading path.
2. Boot Linux to a console without touching GPU modules; verify RAM, storage and Ethernet first.
3. Build and load `xegpu.ko` **against exactly that running kernel**, then run upstream EDRAM initialization and minimal rendering tests.
4. Apply the **entire matching Mesa patch series** to the source revision documented upstream (its README names Mesa base `ab1502f`). Do not apply partial patches or substitute random releases.
5. Cross-build Mesa for **big-endian ppc64** using upstream `mesa/mesa-ppc64-cross.ini`, adapted to your sysroot.
6. Build the big-endian glamor patch against the matching Xorg-server version and launch upstream's IceWM configuration.
7. Run a small GLES probe before larger automated conformance tests. Always have a physical recovery path.

Detailed commands: [upstream setup instructions](https://github.com/arelyx/xenos-linux-gpu/blob/main/docs/setup.md). Do **not** run their optional Peer Pressure softmod changes or system installation commands without verifying differences on your console.

## Known limitations and security notes

- A runaway shader can require **physical power cycling**. Reliable GPU reset has not been demonstrated.
- Its tested presentation mode is **HDMI 720p**. More video modes remain an open task.
- **4 KB pages** improve available RAM but exhibited boot/runtime freezes; 64 KB-page kernels are the safer research baseline.
- The GPU patch modifies Linux VMX handling: Xenon's VMX128 lacks some AltiVec instructions. Never enable generic runtime AltiVec detection without validating the patch.
- `xegpu` defaults to a large contiguous memory pool. Keeping sufficient RAM free is critical.
- 3D acceleration is experimental: **no Vulkan, OpenGL 2.1+, full modern browser support or universal game support**.
- HDMI audio was not audibly validated in the upstream handoff.
- Original upstream authors explicitly described the GPU code as **AI-driven experimental research, not production-reviewed code**. Our project does not claim upstream endorsement.

## Licensing

The upstream GPU repository mixes GPL-2.0-only, MIT/X11, Apache-2.0 and CC BY 4.0 material. Do not copy it under X360Linux's Apache-2.0 license. Keep attribution and original licensing; see [UPSTREAM-AND-LICENSES.md](UPSTREAM-AND-LICENSES.md).
