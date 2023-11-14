# DATA
# python simulate/refine.py


mkdir simul


# SIMULATION
RES_PATH="./simul/"
REPEAT=100
# CHAIN=("ETHEREUM" "POLYGON")
CHAIN=("ETHEREUM")

# Default values
python simulate/nodes.py --verbose 0 --repeat ${REPEAT} > ${RES_PATH}normal.txt

for C in ${CHAIN[@]}; do
    SIZE=$([ ${C} == "ETHEREUM" ] && echo 155 || echo 72)
    INTERVAL=$([ ${C} == "ETHEREUM" ] && echo 12.06 || echo 2.07)

    # DIFF test
    DIFF=(32 128)  # Higher == Easier
    for D in ${DIFF[@]}; do
        TIMEOUT=(10 15 20 25)  # Various TIMEOUT
        for QTO in ${TIMEOUT[@]}; do
            echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qto ${QTO} --size ${SIZE} --interval ${INTERVAL} --d ${D}
            python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qto ${QTO} --size ${SIZE} --interval ${INTERVAL} --d ${D} > ${RES_PATH}${C}_D_${D}_QTO_${QTO}.txt
        done

        QUORUM=(5 10 15 21)  # Various QUORUM
        for QC in ${QUORUM[@]}; do
            echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} --d ${D}
            python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} --d ${D} > ${RES_PATH}${C}_D_${D}_QC_${QC}.txt
        done
    done

    # FREQ test
    FREQ=(0.100 0.050 0.010 0.005 0.001)
    for F in ${FREQ[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL}
        python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_F_${F}.txt
    done

    # BYZANTINE test
    BYZANTINE=(0 5 10 11 15 20 21)  # 5 10 15 21
    for B in ${BYZANTINE[@]}; do
        # default QUORUM 11
        QUORUM=(5 10 11 15 21)
        for QC in ${QUORUM[@]}; do
            echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --byz ${B} --qc ${QC} --size ${SIZE} --interval ${INTERVAL}
            python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --byz ${B} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_B_${B}_QC_${QC}.txt
        done
    done
done


# for C in ${CHAIN[@]}; do
#     SIZE=$([ ${C} == "ETHEREUM" ] && echo 155 || echo 72)
#     INTERVAL=$([ ${C} == "ETHEREUM" ] && echo 12.06 || echo 2.07)

#     FREQ=(0.001 0.005 0.010 0.050 0.100) # TPS test
#     for F in ${FREQ[@]}; do
#         echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL}
#         python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_F_${F}.txt
#     done

#     TIMEOUT=(10 15 20 25)
#     for QTO in ${TIMEOUT[@]}; do
#         echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qto ${QTO} --size ${SIZE} --interval ${INTERVAL}
#         python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qto ${QTO} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_QTO_${QTO}.txt
#     done

#     QUORUM=(5 10 15 21)
#     for QC in ${QUORUM[@]}; do
#         echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qc ${QC} --size ${SIZE} --interval ${INTERVAL}
#         python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_QC_${QC}.txt
#     done

#     DIFF=(64 128 192 256)  # Higher == Easier
#     for D in ${DIFF[@]}; do
#         echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --d ${D} --size ${SIZE} --interval ${INTERVAL}
#         python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --d ${D} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_D_${D}.txt
#     done

#     EPOCH=(2 4 8 16)
#     for E in ${EPOCH[@]}; do
#         echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --epoch ${E} --size ${SIZE} --interval ${INTERVAL}
#         python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --epoch ${E} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_E_${E}.txt
#     done
# done
