
import argparse
import pathlib

from nnttpy import vmtranslator


def main() -> None:
    # Input path
    cml_parser = argparse.ArgumentParser()
    cml_parser.add_argument("--input", type=str, help="Input file path.")
    args = cml_parser.parse_args()
    input_path = pathlib.Path(args.input)

    translator = vmtranslator.VMTranslator()
    assemle_code = translator.translate(input_path)

    # Write parsed binary to file
    output_path = input_path.parent / (input_path.stem + ".asm")
    with output_path.open("w") as f:
        f.write("\n".join(assemle_code))


if __name__ == "__main__":
    main()
