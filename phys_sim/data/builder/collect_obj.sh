#!/usr/bin/env bash

CONTENT_ROOT=/Users/jillianross/ResearchProjects/vil/ADEPT-Dataset-Release
shape_net_folder=/Users/jillianross/Desktop/ShapeNetCore.v2
sim_object_folder=${CONTENT_ROOT}/phys_sim/data/additional_shapes


cat_count=0
for cat_folder in ${shape_net_folder}/*; do
    mkdir ${sim_object_folder}/$(printf "%04d" ${cat_count})
    shape_count=0
    for obj_folder in ${cat_folder}/*; do
        model_file=${obj_folder}/models/model_normalized.obj
        if [[ -e ${model_file} ]]
        then
            cp ${model_file} ${sim_object_folder}/$(printf "%04d" ${cat_count})/$(printf "%06d" ${shape_count}).obj &
            shape_count=$(($shape_count+1))
            echo ${shape_count}
        fi
    done
    cat_count=$(( cat_count+1 ))
done

echo -e '\a\a \a \a\a\a'
