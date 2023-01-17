for i in {51..100..1}
do
    echo exp ${i} start.

    CUDA_VISIBLE_DEVICES=1 python test.py > results/${i}.txt
    # echo Hello > results/${i}.txt

    echo exp ${i} done.
done
