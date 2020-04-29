i=1
for port in `cat port.yml`
do 
    if [ $i -eq 1 ]
    then
       env=$port
    elif [ $i -eq 2 ] 
    then
       shutdown=$port
    elif [ $i -eq 3 ]
    then
       ajp=$port
    elif [ $i -eq 4 ]
    then
       http=$port
    elif [ $i -eq 5 ]
    then
       https=$port
#       ansible-playbook -i ../inventory updateXML.yml --extra-vars "var_host=sytas env=$env http=$http https=$https ajp=$ajp shutdown=$shutdown" -K
echo $i
       i=0
    fi
i=$[$i+1]
done
