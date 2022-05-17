# 1..768
for i in {700..768}
do
  if [ ! -f "quests/$i/data.json" ]
  then
    rm -rf output
    python3 src/main.py quests/"$i"/*.qst
    mv output/* "quests/$i"
  fi
done
