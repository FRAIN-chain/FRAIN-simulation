# python simulate/refine.py

# ======

# SIMULATION

RES_PATH="./results/simul/"

# CHAIN=("ETHEREUM" "POLYGON")
CHAIN=("ETHEREUM")

for C in ${CHAIN[@]}; do
    SIZE=$([ ${C} == "ETHEREUM" ] && echo 155 || echo 72)
    INTERVAL=$([ ${C} == "ETHEREUM" ] && echo 12.06 || echo 2.07)

    FREQ=(0.001 0.005 0.010 0.050 0.100) # TPS test
    for F in ${FREQ[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat 10 --freq ${F}
        python simulate/nodes.py --verbose 0 --repeat 10 --freq ${F} > ${RES_PATH}${C}_F_${F}.txt
    done

    TIMEOUT=(5 7 9 10)
    for TC in ${TIMEOUT[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat 10 --tc ${TC} --size ${SIZE} --interval ${INTERVAL}
        python simulate/nodes.py --verbose 0 --repeat 10 --tc ${TC} > ${RES_PATH}${C}_TC_${TC}.txt
    done

    QUORUM=(5 13 21)
    for QC in ${QUORUM[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat 10 --qc ${QC} --size ${SIZE} --interval ${INTERVAL}
        python simulate/nodes.py --verbose 0 --repeat 10 --qc ${QC} > ${RES_PATH}${C}_QC_${QC}.txt
    done

    DIFF=(64 128 192 256)  # Higher == Easier
    for D in ${DIFF[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat 10 --d ${D} --size ${SIZE} --interval ${INTERVAL}
        python simulate/nodes.py --verbose 0 --repeat 10 --d ${D} > ${RES_PATH}${C}_D_${D}.txt
    done

    EPOCH=(2 4 8)
    for E in ${EPOCH[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat 10 --epoch ${E} --size ${SIZE} --interval ${INTERVAL}
        python simulate/nodes.py --verbose 0 --repeat 10 --epoch ${E} > ${RES_PATH}${C}_E_${E}.txt
    done
done
