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
    parser.add_argument('-o','--output', default='./output/',
                        help='Output directory, will overwrite existing directory (default: ./output/)')
    parser.add_argument('--tile-length', type=int,
                        help='If provided, splits the pointcloud into tile-length by tile-length tiles')
    parser.add_argument('--cloud-compare', action='store_true',
                        help='Use cloud compare headless to instead of pdal (default: False)')
    # parser.add_argument('--no-convert', action='store_false',
    #                     help='Change ply and las files to laz for faster transfers (default: True)')
    parser.add_argument('-p','--pipeline', default='pipeline.json',
                        help='Sets the  (default: pipeline.json)')
    parser.add_argument('--benchmark', action='store_true',
                        help='Loops through all available nodes and creates a report (default: False)')

    
    return parser
