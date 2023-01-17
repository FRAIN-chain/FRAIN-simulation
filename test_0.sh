for i in {1..50..1}
do
    echo exp ${i} start.

    CUDA_VISIBLE_DEVICES=0 python test.py > results/${i}.txt
    # echo Hello > results/${i}.txt

    echo exp ${i} done.
done
