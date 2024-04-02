# DATA
# python simulate/refine.py


# sh simul_clean.sh
rm -rf simul/
rm -rf save
mkdir simul
mkdir save
mkdir save/objects


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

    # FREQ test
    FREQ=(1.0 0.100 0.050 0.010 0.005 0.001)
    for F in ${FREQ[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL}
             python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_F_${F}.txt
    done

    # DIFF test
    DIFF=(32 128)  # Higher == Easier
    for D in ${DIFF[@]}; do
        # QUORUM
        QUORUM=(5 10 15 20)
        for QC in ${QUORUM[@]}; do
            echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} --d ${D}
                 python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} --d ${D} > ${RES_PATH}${C}_D_${D}_QC_${QC}.txt
        done

        # TIMEOUT
        TIMEOUT=(10 15 20 25)
        for QTO in ${TIMEOUT[@]}; do
            echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qto ${QTO} --size ${SIZE} --interval ${INTERVAL} --d ${D}
                 python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --qto ${QTO} --size ${SIZE} --interval ${INTERVAL} --d ${D} > ${RES_PATH}${C}_D_${D}_QTO_${QTO}.txt
        done
    done

    # BYZANTINE test
    BYZANTINE=(0 5 10 11 15)  # 5 10 15 21
    for B in ${BYZANTINE[@]}; do
        # QUORUM
        QUORUM=(5 10 11 15 20)
        for QC in ${QUORUM[@]}; do
            echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --byz ${B} --qc ${QC} --size ${SIZE} --interval ${INTERVAL}
                 python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --byz ${B} --qc ${QC} --size ${SIZE} --interval ${INTERVAL} > ${RES_PATH}${C}_B_${B}_QC_${QC}.txt
        done
    done
done
