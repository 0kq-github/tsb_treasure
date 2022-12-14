import glob
import os
import re
import json
import shutil
import nbtlib

treasure_list = glob.glob("./sacred_treasure/*")
output_folder = "./export/"
#functions = glob.glob("./sacred_treasure/**/*/2.give.mcfunction")


def getvalue(v,text) -> str:
  try:
    return re.search(f"(?<=data modify storage asset:sacred_treasure {v} set value ).*?(?=\n)",text).group()
  except:
    return None

def getpathall(text) -> list:
  return re.findall("(?<=data modify storage asset:sacred_treasure ).*?(?= set value)",text)

def text_replace(text):
  result = {}
  path = getpathall(text)
  for i in path:
    result[i] = getvalue(i,text)
  return result


def filter_text(a,path):
  """
  a: ファイル名
  path: 神器のストレージのパス
  """
  with open(a,"r",encoding="utf-8") as f:
    try:
      replaced = text_replace(f.read())[path]
    except KeyError:
      return None
    if not replaced:
      return replaced
    print(replaced)
    nbt = nbtlib.parse_nbt(replaced)
    result_list = []
    if (path == "Name") or (path == "Lore"):
      if isinstance(nbt,list):
        for i in nbt:
          if (i[0] == "[") or (i[-1] == "]"):
            i = i.lstrip("[").rstrip("]")
            i = "[" + i + "]"
          j = json.loads(i)
          if isinstance(j,list):
            for v in j:
              result_list.append(v["text"])
              #print(v["text"])
          elif isinstance(j,dict):
            if "text" in j.keys():
              result_list.append(j["text"])
          else:
            continue
      else:
        j = json.loads(nbt)
        if isinstance(j,list):
          for i in j:
            if "text" in i.keys():
              result_list.append(i["text"])
        else:
          result_list.append(j["text"])
        #print(j["text"])
      return "".join(result_list)
    elif (path == "CostText") and (replaced != None):
      if not isinstance(nbt,str):
        return nbt
      j = json.loads(nbt)
      result_list = []
      for i in j:
        if "translate" in i.keys():
          result_list.append(i["translate"])
        elif "text" in i.keys():
          result_list.append(i["text"])
      return "".join(result_list)
    elif path == "CanUsedGod":
      goddict = {"Urban":"アーバン","Flora":"フローラ","Nyaptov":"ニャプトフ","Rumor":"ルーモア","Wi-ki":"ウィ=キ"}
      if nbt == "ALL":
        return " ".join(goddict.values())
      #j = json.loads(nbt)
      if isinstance(nbt,list):
        godlist = [str(v) for v in nbt]
      result = []
      for i in godlist:
        result.append(goddict[i])
      return " ".join(result)
    else:
      return replaced

def trigger(i):
  Trigger = filter_text(i,"Trigger").strip("\"").strip("\'")
  Slot = filter_text(i,"Slot").strip("\"").strip("\'")
  text = ""

  if Trigger == "onClick":
    text = "右クリック"
  if Trigger == "itemUse":
    text = "アイテムを使用"
  if Slot == "mainhand":
    if Trigger == "onAttackByMelee":
      text = "メインハンドに所持しEntityを近接攻撃"
    if Trigger == "sneak1s":
      text = "メインハンドに所持し1秒間スニーク"
    if Trigger == "keepSneak":
      text = "メインハンドに所持し0秒以上スニーク"
    if Trigger == "onKilledByMelee":
      text = "メインハンドに所持しEntityを近接攻撃で殺害"
    if Trigger == "onAttack":
      text = "メインハンドに所持しEntityを攻撃"
  if Slot == "offhand":
    if Trigger == "onAttackByMelee":
      text = "オフハンドに所持しEntityを近接攻撃"
    if Trigger == "passive":
      text = "オフハンドに所持している限り"
  if (Slot == "head" or  "chest" or "legs" or "feet"):
    if Trigger == "onAttackByMelee":
      text = "装備しEntityを近接攻撃"
    if Trigger == "equipping":
      text = "装備"
    if Trigger == "onDamageFromEntity":
      text = "装備し被攻撃ダメージ"
    if Trigger == "passive":
      text = "装備している限り"
    if Trigger == "onDamage":
      text = "装備し被ダメージ"

  return text


if __name__ == "__main__":
  shutil.rmtree(f"{output_folder}",ignore_errors=True)
  for l in treasure_list:
    i = l+"/give/2.give.mcfunction"
    rarity = "0"
    if os.path.exists(l+"/register.mcfunction"):
      with open(l+"/register.mcfunction","r",encoding="utf-8") as lf:
        rarity = re.search("(?<=data modify storage asset:sacred_treasure RarityRegistry\[).*?(?=\] append value)",lf.read()).group()
    if not os.path.exists(f"{output_folder}"):
      os.makedirs(f"{output_folder}")
    if not os.path.exists(f"{output_folder}/treasure_{rarity}.csv"):
      with open(f"{output_folder}/treasure_{rarity}.csv","w",encoding="utf-8") as f:
        f.write("神器名,アイテム説明,使用方法,使用回数,MP消費量,MP必要量,消費アイテム,CT,グローバルCT,対応信仰神\n")
    with open(f"{output_folder}/treasure_{rarity}.csv","a",encoding="utf-8") as f:
      text = f'{filter_text(i,"Name")},{filter_text(i,"Lore")},{trigger(i)},{filter_text(i,"RemainingCount")},{filter_text(i,"MPCost")},{filter_text(i,"MPRequire")},{filter_text(i,"CostText")},{filter_text(i,"LocalCooldown")},{filter_text(i,"SpecialCooldown")},{filter_text(i,"CanUsedGod")}\n'
      print(filter_text(i,"Name"))
      f.write(text)






