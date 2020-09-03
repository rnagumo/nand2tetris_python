
import argparse
import pathlib

from nnttpy import assembler


def main() -> None:
    # Input path
    cml_parser = argparse.ArgumentParser()
    cml_parser.add_argument("--input", type=str, help="Input file path.")
    args = cml_parser.parse_args()
    input_path = pathlib.Path(args.input)

    # Read file
    with input_path.open("r") as f:
        lines = f.readlines()

    # Assemble
    hack_assembler = assembler.Assembler(lines)
    binary = hack_assembler.assemble()

    # Write parsed binary to file
    output_path = input_path.parent / (input_path.stem + ".hack")
    with output_path.open("w") as f:
        f.write("\n".join(binary))


if __name__ == "__main__":
    main()
