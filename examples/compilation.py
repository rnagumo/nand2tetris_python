
import argparse
import pathlib

from nnttpy import jackcompiler


def main() -> None:
    # Input path
    cml_parser = argparse.ArgumentParser()
    cml_parser.add_argument("--input", type=str, help="Input file path.")
    cml_parser.add_argument("--xml", action="store_true",
                            help="Whether output is XML or not.")
    args = cml_parser.parse_args()
    input_path = pathlib.Path(args.input)

    if input_path.is_dir():
        path_list = list(input_path.glob("*.jack"))
        if not path_list:
            raise ValueError(f"No .jack file is found in {input_path}")
    else:
        path_list = [input_path]

    # Compile
    for path in path_list:
        compiler = jackcompiler.JackAnalyzer()
        if args.xml:
            output = compiler.compile_xml(path)
        else:
            output = compiler.compile(path)

        output_path = path.parent / (path.stem + ".xml")
        with output_path.open("w") as f:
            f.write("\n".join(output))


if __name__ == "__main__":
    main()
