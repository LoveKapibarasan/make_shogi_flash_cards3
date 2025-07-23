import shogi
import os
import sys
import json

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import from sibling dir_b

from Engines.engines_management import initialize_engine, read_output 
INPUT_FOLDER = "analyze_kif/input_json_files"
OUTPUT_FOLDER = "analyze_kif/output_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def analyze_kif():
    proc = initialize_engine()
    for file_name in os.listdir(INPUT_FOLDER):
        if not file_name.endswith(".json"):
            continue
        input_file_path = os.path.join(INPUT_FOLDER, file_name)
        output_file_path = os.path.join(OUTPUT_FOLDER, file_name)
        with open(input_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for node in data["nodes"]:
            sfen = node["sfen"]
            if node.get("cp") is not None and node.get("pv"):
                continue
            command = f"position sfen {sfen}"
            print("[DEBUG] Command:", command)

            cp, nodes, pv = read_output(proc, command)
                
            # Process PV
            pv_sfen_list = []
            board = shogi.Board(sfen)
            
            for p in pv.split()[:4]:
                board.push_usi(p)
                pv_sfen_list.append(board.sfen())
            
            # Update node with cp and pv
            node["cp"] = cp
            node["pv"] = pv_sfen_list

            # Save entire modified data after processing all nodes
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    analyze_kif()