mkdir -p quests

for i in {1..768}
do
  if [ ! -d "quests/$i" ]
  then
    wget "https://www.purezc.net/index.php?page=download&section=Quests&id=$i" -O temp.zip
    mkdir -p "quests/$i"
    unzip -d "quests/$i" temp.zip
    rm temp.zip
  fi
done
