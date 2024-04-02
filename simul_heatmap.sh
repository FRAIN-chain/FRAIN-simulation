# sh simul_heatmap_clean.sh
rm -rf simul_heatmap/
rm -rf save_heatmap
mkdir simul_heatmap
mkdir save_heatmap
mkdir save_heatmap/objects


# SIMULATION
RES_PATH="./simul_heatmap"
REPEAT=1
# CHAIN=("ETHEREUM" "POLYGON")
CHAIN=("ETHEREUM")
QTO=0  # 0 for infinity

for C in ${CHAIN[@]}; do
    SIZE=$([ ${C} == "ETHEREUM" ] && echo 155 || echo 72)
    INTERVAL=$([ ${C} == "ETHEREUM" ] && echo 12.06 || echo 2.07)

    DIFF=(16 32 64 128)  # Higher == Easier
    for D in ${DIFF[@]}; do

        QUORUM=(5 10 15 20)
        for QC in ${QUORUM[@]}; do

            EPOCH=(1 2 4 8 16)
            for E in ${EPOCH[@]}; do
                echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --epoch ${E} --qc ${QC} --d ${D} --size ${SIZE} --interval ${INTERVAL} --path "./save_heatmap" --qto ${QTO}
                     python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --epoch ${E} --qc ${QC} --d ${D} --size ${SIZE} --interval ${INTERVAL} --path "./save_heatmap" --qto ${QTO} > ${RES_PATH}/${C}_E${E}_QC${QC}_D${D}_QTO${QTO}.txt
            done
        done
    done
done


# Visualization
python visualization/heatmap.py
