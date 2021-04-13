# stdin, stdout, stderr = ssh.exec_command(command)

# lines = stdout.readlines()

# print(lines)
import sys

from utils.utils import check_requirements, get_nodes, init_argparse

if __name__ == '__main__':
    check_requirements()

    parser = init_argparse()

    args = parser.parse_args()

    if len(args.files) == 0:
        print("No files provided, exiting...")
        sys.exit()
    
    print(f"{len(args.files)} files provided, {args.files}")
        
    nodes = get_nodes()

    for node in nodes:
        node.setup()
    print(nodes)