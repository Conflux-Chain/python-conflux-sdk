import json, os

ipynb_dir = "./examples/ipynb"
py_dir = "./examples/py"

src_files = os.listdir(ipynb_dir)

for file in src_files:
    code = json.load(open(os.path.join(ipynb_dir, file)))
    if not os.path.exists(py_dir):
        os.mkdir(py_dir)
    py_file = open(f"{os.path.join(py_dir, file.replace('ipynb', 'py'))}", "w+")

    for cell in code['cells']:
        if cell['cell_type'] == 'code':
            for line in cell['source']:
                py_file.write(line)
            py_file.write("\n\n")
        elif cell['cell_type'] == 'markdown':
            # py_file.write("\n")
            for line in cell['source']:
                # if line and line[0] == "#":
                #     py_file.write(line)
                py_file.write(f"# {line}")
            py_file.write("\n")
            py_file.write("\n")

    py_file.close()
