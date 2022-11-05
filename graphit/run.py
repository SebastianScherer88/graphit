from utils.run_helpers import parse_graphit_arguments, run_graphit


def main():

    # get all arguments required for running graphit on the given project
    command_line_args = parse_graphit_arguments()

    run_graphit(command_line_args)

    return

if __name__ == '__main__':
    main()