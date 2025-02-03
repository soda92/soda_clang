import argparse
from pathlib import Path
import functools
import subprocess
import os


def which(name):
    path = os.environ["PATH"]
    for p in path.split(";"):
        exe = Path(p).joinpath(name)
        if exe.exists():
            return exe


@functools.cache
def get_gcc_path():
    out = which("gcc.exe")
    return out.resolve().parent.parent


def str_path(p: Path):
    return str(p).replace("\\", "/")


def main(cxx=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=str, nargs="*", default=[], help="sources")
    parser.add_argument(
        "--include", "-I", type=str, action="append", default=[], help="include path"
    )
    parser.add_argument("--output", "-o", type=str, default="a.exe", help="output")
    parser.add_argument(
        "--link", "-l", type=str, action="append", default=[], help="link"
    )
    parser.add_argument(
        "--library",
        "-L",
        type=str,
        action="append",
        default=[],
        help="library search path",
    )

    args = parser.parse_args()

    # print(args.include, args.output, args.link, args.library)
    # print(args.sources)
    sources = args.sources

    gcc_path: Path = get_gcc_path()

    cmdline = ["clang", "-c"]
    if cxx:
        cmdline = ["clang++", "-c"]
    targets = []
    for source in sources:
        cmdline.append(source)
        target = Path(source).stem + ".o"
        targets.append(target)
        cmdline.extend(["-o", target])
        includes = []
        for i in args.include:
            includes.append("-I" + i)
        cmdline.extend(includes)
        if not cxx:
            c_includes = ["x86_64-w64-mingw32/include"]
            for i in c_includes:
                cmdline.append(f"-I{str_path(gcc_path.joinpath(i))}")
        else:
            cxx_includes = [
                "include/c++/13.2.0/x86_64-w64-mingw32",
                "include/c++/13.2.0",
                "x86_64-w64-mingw32/include",
            ]
            for i in cxx_includes:
                cmdline.append(f"-I{str_path(gcc_path.joinpath(i))}")
        cmdline.append("-Wno-ignored-attributes")
        # print(" ".join(cmdline))
        subprocess.run(cmdline, check=True)

    libs = "-lmingw32 -lmoldname -lmingwex -lmsvcrt -ladvapi32 -lshell32 -luser32 -lkernel32 -lgcc".split()
    libs.extend(args.link)
    link_cmd = [
        str_path(gcc_path.joinpath("bin/ld.exe")),
        "-m",
        "i386pep",
        "-Bdynamic",
    ]
    search_paths = [
        "x86_64-w64-mingw32/lib",
        "lib/gcc/x86_64-w64-mingw32/13.2.0/",
    ]
    search_paths.extend(args.library)
    if cxx:
        search_paths.append("lib")

    for i in search_paths:
        link_cmd.append(f"-L{str_path(gcc_path.joinpath(i))}")

    crt_objects = [
        "x86_64-w64-mingw32/lib/crt2.o",
        "x86_64-w64-mingw32/lib/crtbegin.o",
        "x86_64-w64-mingw32/lib/crtend.o",
    ]

    for i in crt_objects:
        link_cmd.append(str_path(gcc_path.joinpath(i)))

    for t in targets:
        link_cmd.append(t)

    link_cmd.extend(libs)
    if cxx:
        link_cmd.append("-lstdc++")

    link_cmd.append("-o")
    link_cmd.append(args.output)
    if cxx:
        link_cmd.extend(
            "-lmingw32 -lgcc -lmoldname -lmingwex -lmsvcrt -lkernel32 -lpthread -ladvapi32 -lshell32 -luser32 -lkernel32 -lmingw32 -lgcc -lmoldname -lmingwex -lmsvcrt".split()
        )

    # print(" ".join(link_cmd))
    # Path("cmd").write_text(" ".join(link_cmd), encoding="utf8")
    subprocess.run(link_cmd, check=True)


def main_cxx():
    main(cxx=True)


if __name__ == "__main__":
    main()
