import os
import argparse

def get_files_with_extensions(directory, extensions):
    """
    Recursively get all files with the specified extensions in the given directory.
    """
    matched_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.split('.')[-1] in extensions:
                matched_files.append(os.path.join(root, file))
    return matched_files

def read_file_content(file_path):
    """
    Read the content of a file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_output_file(files, output_file='code.txt'):
    """
    Write the content of each file in a code block format to the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for file in files:
            content = read_file_content(file)
            out_file.write(f"```{file}\n{content}\n```\n\n")

def main():
    parser = argparse.ArgumentParser(description="Collect content of specified files and write to output.txt")
    parser.add_argument('-d', '--directory', required=True, help="Directory to search files in")
    parser.add_argument('-e', '--extensions', required=True, help="Comma-separated list of file extensions to include")

    args = parser.parse_args()
    directory = args.directory
    extensions = args.extensions.split(',')

    files = get_files_with_extensions(directory, extensions)
    write_output_file(files)

if __name__ == "__main__":
    main()
