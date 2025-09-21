RES_PATH="./simul/"
REPEAT=100


# cnn / slm
TL=(0.4037 10.9165)
for T in ${TL[@]}; do
    SIZE=210
    INTERVAL=12.06

    # FREQ test
    FREQ=(1.0 0.100 0.0577 0.050 0.010 0.005 0.001)
    for F in ${FREQ[@]}; do
        echo python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL} --training ${T}
             python simulate/nodes.py --verbose 0 --repeat ${REPEAT} --freq ${F} --size ${SIZE} --interval ${INTERVAL} --training ${T} > ${RES_PATH}${T}_F_${F}.txt
    done
done
