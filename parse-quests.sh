# 1..768
for i in {700..768}
do
  if [ ! -f "quests/$i/data.json" ]
  then
    rm -rf output
    ./docker_run.sh quests/"$i"/*.qst
    mv output/* "quests/$i"
  fi
done
