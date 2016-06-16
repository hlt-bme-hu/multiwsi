list="hom/en.hom.list"
field=7

if [[ -n $1 ]]
then
 list=$1
fi

if [[ -n $2 ]]
then
 field=$2
fi

while read f1
do
 echo -n "$f1 "
 found=0
 while read f2
 do
  if [[ $found -eq 0 ]]
  then
   if [[ ! $f1 == $f2 ]]
   then
    echo -n " &"
   else
    echo -n " & 1.0"
    found=1
   fi
  else
   echo -n " & `python script/compare_sense_counts.py $f1 $f2 | tail -n 1 | cut -f$field -d" "`"  
  fi
 done < $list
 echo
done < $list
