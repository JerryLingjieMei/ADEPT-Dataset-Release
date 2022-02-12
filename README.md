# ADEPT-Dataset-Release

This is the dataset generation code for ADEPT (Approximate Derenderer, Extended Physics, and Tracking).

![](assets/data.jpg)

Modeling Expectation Violation in Intuitive Physics with Coarse Probabilistic Object Representations

Kevin Smith*, Lingjie Mei*, Shunyu Yao, Jiajun Wu, Elizabeth S. Spelke, Joshua B. Tenenbaum, Tomer Ullman  (* indicates equal contribution)

NeurIPS 2019, CogSci 2020

[Paper](http://physadept.csail.mit.edu/papers/adept.pdf) [BibTeX](http://physadept.csail.mit.edu/bibtex/adept.bib) [Website](http://physadept.csail.mit.edu/)

For the model, see [ADEPT-Model-Release](https://github.com/JerryLingjieMei/ADEPT-Model-Release)
## Prerequisites
- Linux
- Python3
- Blender as a python module
- Other modules required specified in `requirements.txt`

## Getting started
1. Clone this directory

    ```bash
    git clone https://github.com/JerryLingjieMei/ADEPT-Dataset-Release
    cd ADEPT-Dataset-Release
    ```
    
    And replace `CONTENT_FOLDER` in `utils.constants` and `phys_sim/data/builder/collect_obj.sh` 
    with the absolute path to your directory.
    
1. Create a conda environment for ADEPT Dataset Generation,
 and install the requirements. 
 
    ```bash
    conda create --n adept-dataset
    conda activate adept-dataset
    pip install -r requirements.txt
    ```
 
 For installation of Blender as a python module, see [Blender wiki](https://wiki.blender.org/wiki/Building_Blender/Linux/Ubuntu).
    
    You may also try using Blender's bundled python, by replacing `python *.py --arg1 --value1` with `blender -b --python -- --arg1 --value1`

1. (Optional) If you have multiple machines, you may change `get_host_id` in `utils/misc.py` 
to reflect the id of your machine. With that in hand, you may speed up all following processes by using `--stride N` arguments, where you have `N` machines with consecutive ids.

1. To render ShapeNet objects, please download ShapeNet Core V2 from its [official website](https://www.shapenet.org/). 
Change `SHAPE_NET_FOLDER` in `phys_sim/data/builder/collect_obj.sh` to the path of ShapeNet meshes, and run thar script.

    To turn them into `.blend` files, run
    ```bash
    # Single machine
    python3 render/data/builder/collect_blend.py #Map phase
    python3 render/data/builder/collect_blend.py --reduce #Reduce phase
    # Multiple (e.g. 8) machines
    python3 render/data/builder/collect_blend.py --stride 8 #On each machine
    python3 render/data/builder/collect_blend.py --reduce --stride 8 #On a single machine
    ```

## Dataset generation
1. Generate training set (e.g. with 1000 videos) by running
    ```bash
    # Single machine
    python3 dataset/generate_train.py --end 1000
    # Multiple (e.g. 8) machines
    python3 dataset/generate_train.py --end 1000 --stride 8 #On each machine
    ```
    
1. Generate human test set by running
    ```bash
    # Single machine
    python3 dataset/human/generate_human.py --end 1000
    # Multiple (e.g. 8) machines
    python3 dataset/human/generate_human.py --end 1000 --stride 8 #On each machine
    ```

## Evaluation

1. Evaluating the relative accuracy on human test set. 
If you have a experiment output folder that contains `.txt` files containing the scores of all human test cases, run
    ```bash
    python3 dataset/human/collect_reuslts.py --summary_folder ${SUMMARY_FOLDER} #Score in SUMMARY_FOLDER/results
    python3 dataset/human/collect_reuslts.py --summary_folder ${SUMMARY_FOLDER} --output_folder ${OUTPUT_FOLDER} #Custom output folder
    ```
    Or you may get the relative accuracy from a json file that contains a dictionary mapping case name to its score:
    ```bash
    python3 dataset/human/collect_results.py --summary_file ${SUMMARY_FILE} --output_folder ${OUTPUT_FOLDER} #Custom output folder
    ```

