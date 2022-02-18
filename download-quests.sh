mkdir -p quests

# 1..768
for i in {1..100}
do
  if [ ! -d "quests/$i" ]
  then
    wget "https://www.purezc.net/index.php?page=download&section=Quests&id=$i" -O temp.zip
    mkdir -p "quests/$i"
    unzip -d "quests/$i" temp.zip
    rm temp.zip
  fi
done
