# ADEPT-Dataset-Release

This is the dataset generation code for ADEPT (Approximate Derenderer, Extended Physics, and Tracking).

![](assets/data.jpg)

Modeling Expectation Violation in Intuitive Physics with Coarse Probabilistic Object Representations

Kevin Smith*, Lingjie Mei*, Shunyu Yao, Jiajun Wu, Elizabeth S. Spelke, Joshua B. Tenenbaum, Tomer Ullman  (* indicates equal contribution)

NeurIPS 2019, CogSci 2020

[Paper](http://physadept.csail.mit.edu/papers/adept.pdf) [BibTeX](http://physadept.csail.mit.edu/bibtex/adept.bib) [Website](http://physadept.csail.mit.edu/)

For the model, see [ADEPT-Model-Release](https://github.com/JerryLingjieMei/ADEPT-Model-Release)
 
## Getting started

1. Clone this directory and create a conda environment for ADEPT Dataset Generation.

    ```bash
    git clone https://github.com/JerryLingjieMei/ADEPT-Dataset-Release
    cd ADEPT-Dataset-Release
    conda create -n adept-dataset python=3.10
    conda activate adept-dataset
    ```

2. Run the setup script, which install Blender 3.1.2 and python packages used in the scripts.
   ```bash
    bash install.sh
    ```
3. Configure the `ffmpeg` in `dataset.make_video` to the one used by your system.
1. (Optional) By default, the script in run on one machine only. Set up `get_host_id` in `util.misc` to run the job on multiple devices. Append to each script with `--stride` argument will enable job assignment.
2. (Optional) 
    + ShapeNet objects are by default not included unless the scripts below are run.

    + To render ShapeNet objects, please download ShapeNet Core V2 from its [official website](https://www.shapenet.org/). 
Change `SHAPE_NET_FOLDER` in `phys_sim/data/builder/collect_obj.sh` to the path of ShapeNet meshes, and run thar script. To turn them into `.blend` files, run
   ```bash
    # Single machine
    ./blender/blender --background --python render/data/builder/collect_blend.py #Map phase
    ./blender/blender --background --python render/data/builder/collect_blend.py -- --reduce #Reduce phase
    # Multiple machines
    ./blender/blender --background --python render/data/builder/collect_blend.py -- --stride 8 #On each machine
    ./blender/blender --background --python render/data/builder/collect_blend.py -- --reduce --stride 8 #On a single machine
    ```
    
## Dataset generation
1. Generate training set (e.g. with 1000 videos) by running
    ```bash
    # Single machine
    ./blender/blender --background --python dataset/generate_train.py --end 1000 --
    # Multiple machines
    ./blender/blender --background --python dataset/generate_train.py --end 1000 -- --stride 8 #On each machine
    ```
    
1. Generate human test set by running
    ```bash
    # Single machine
    ./blender/blender --background --python dataset/human/generate_human.py --
    # Multiple (e.g. 8) machines
    ./blender/blender --background --python ataset/human/generate_human.py -- --stride 8 #On each machine
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

