import argparse

def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(

        usage="%(prog)s [OPTION] [FILE]...",

        description="A tool for pointcloud distributed pipelines. Accepts .ply or .laz as input, will split the files and perform remote processing on them."

    )

    parser.add_argument(

        "-v", "--version", action="version",

        version=f"{parser.prog} version 1.0.0"

    )

    parser.add_argument('files', nargs='*')
    parser.add_argument('--config', default='config',
                        help='Provide an alternative config file (default: config)')
    parser.add_argument('--secret', default='secret',
                        help='Provide an alternative secret file (default: secret)')
    return parser
