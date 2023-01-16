for i in {1..100..1}
do
    echo exp ${i} start.

    python test.py > results/${i}.txt
    # echo Hello > results/${i}.txt

    echo exp ${i} done.
done
