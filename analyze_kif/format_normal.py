import os
import shogi
import shogi.KIF
import json

INPUT_FOLDER = "analyze_kif/input_files"
OUTPUT_FOLDER = "analyze_kif/input_json_files"
ID_file_path = "analyze_kif/ID.txt"



def create_json_files():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    with open(ID_file_path, "r", encoding="utf-8") as f:
        ID = int(f.read().strip())
    # KIFファイルの読み込み
    for file_name in os.listdir(INPUT_FOLDER):
        if file_name.endswith(".kif"):
            input_file_path = os.path.join(INPUT_FOLDER, file_name)
            # まずUTF-8で試し、失敗したらcp932(Shift_JIS)で再試行
            try:
                with open(input_file_path, "r", encoding="utf-8") as f:
                    kif_string = f.read()
            except UnicodeDecodeError:
                with open(input_file_path, "r", encoding="cp932") as f:
                    kif_string = f.read()
       
            # KIFパーサーを生成
            kif = shogi.KIF.Parser.parse_str(kif_string)[0]
            black_player = kif['names'][shogi.BLACK]
            white_player = kif['names'][shogi.WHITE]



            # Board に適用
            board = shogi.Board(kif['sfen'].replace(" w ", " b ")) # This is because of bug in python-shogi
            # KIFの手を1つずつ適用
            counter = 0
            result = []
            for move in kif['moves']:
                sfen = board.sfen()
                result.append({
                    "id": ID,
                    "move": move,
                    "sfen": sfen,
                    "cp": 0,
                    "pv": [],
                    "index": counter,
                    "next_ids": [ID+1],
                    "comment": ""
                })
                counter += 1
                ID = ID + 1
                board.push_usi(move)

            output_data =  {
                "meta": {
                    "id": file_name,
                    "data": {
                        "black_player": black_player,
                        "white_player": white_player,
                    }
                },
                "nodes": result
            }
            
            # JSONファイルに書き込み
            output_file_path = os.path.join(OUTPUT_FOLDER, f"{file_name}.json")
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

    # 最終IDをファイルに保存（オプション）
    with open(ID_file_path, "w", encoding="utf-8") as f:
        f.write(str(ID))

if __name__ == "__main__":
    create_json_files()
    print("JSON files created successfully.")