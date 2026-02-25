import json
import os

songNameLol = input('Enter song name: ').strip()

if not songNameLol:
    raise ValueError("Error: You forgot to enter a song name.")

chart_file = f"{songNameLol}-chart.json"
meta_file = f"{songNameLol}-metadata.json"

if not os.path.isfile(chart_file):
    raise FileNotFoundError(f"Error: Volume 1 Chart file '{chart_file}' not found. Does it exist in your folder?")

if not os.path.isfile(meta_file):
    raise FileNotFoundError(f"Error: Volume 1 Metadata file '{meta_file}' not found. Does it exist in your folder?")

with open(chart_file, "r") as f:
    chart_data = json.load(f)
with open(meta_file, "r") as f:
    meta_data = json.load(f)

psych_chart = {
    "song": {
        "song": meta_data["songName"],
        "notes": [],
        "bpm": meta_data["timeChanges"][0]["bpm"],
        "needsVoices": True,
        "player1": meta_data["player"],
        "player2": meta_data["opponent"],
        "gfVersion": meta_data["gf"],
        "stage": meta_data["stage"],
        "speed": chart_data.get("speed", 1),
        "validScore": True
    }
}

time_changes = sorted(meta_data.get("timeChanges", []), key=lambda x: x["time"])
if not time_changes:
    time_changes = [{"time": 0, "bpm": meta_data.get("bpm", 120)}]
    
def get_bpm_for_time(ms):
    current_bpm = time_changes[0]["bpm"]
    for change in time_changes:
        if ms >= change["time"]:
            current_bpm = change["bpm"]
        else:
            break
    return current_bpm

def ms_per_section(bpm):
    return (60000 / bpm) * 4

last_bpm = time_changes[0]["bpm"]

for section in chart_data["notes"]:
    new_section = {
        "mustHitSection": section["mustHitSection"],
        "sectionNotes": [],
        "lengthInSteps": 16,
        "altAnim": False
    }

    for note in section["notes"]:
        new_note = [
            note["time"],
            note["direction"],
            note.get("length", 0),
            note.get("style", note.get("type", ""))
        ]
        new_section["sectionNotes"].append(new_note)

    if section["notes"]:
        section_start_time = min(n["time"] for n in section["notes"])
    else:
        idx = len(psych_chart["song"]["notes"])
        section_start_time = idx * ms_per_section(last_bpm)

    section_bpm = get_bpm_for_time(section_start_time)

    new_section["bpm"] = section_bpm
    new_section["changeBPM"] = section_bpm != last_bpm

    last_bpm = section_bpm

    psych_chart["song"]["notes"].append(new_section)

psych_chart["song"]["sections"] = len(psych_chart["song"]["notes"])

with open(f"{songNameLol}.json", "w") as f:
    json.dump(psych_chart, f, indent=4)

print("Successfully converted " + psych_chart["song"]["song"] + " to Psych Engine Format!")
input("Press Enter to exit...")
