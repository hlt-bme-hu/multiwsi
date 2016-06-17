echo \
    `wc -l $2 | cut -d' ' -f1`  \
    `head -1 vect-glob-300K | tr , ' ' | wc | sed 's/ \+/\t/g' | cut -f3` \
    > h
cat $2 | tr , ' ' | paste -d' ' $1 - | cat h - 
rm h
