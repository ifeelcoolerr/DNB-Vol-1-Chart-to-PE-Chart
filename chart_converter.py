import json

songNameLol = input('Enter song name: ')

with open(f"{songNameLol}-chart.json", "r") as f:
    chart_data = json.load(f)
with open(f"{songNameLol}-metadata.json", "r") as f:
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
        "sections": len(chart_data["notes"]),
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

last_bpm = time_changes[0]["bpm"]
bpm_change_index = 1 if len(time_changes) > 1 else None
next_bpm_time = time_changes[bpm_change_index]["time"] if bpm_change_index else None

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

    section_start_time = None
    if section["notes"]:
        section_start_time = min(n["time"] for n in section["notes"])
    else:
        idx = len(psych_chart["song"]["notes"])
        section_start_time = idx * 4000

    if next_bpm_time and section_start_time >= next_bpm_time:
        last_bpm = time_changes[bpm_change_index]["bpm"]
        new_section["bpm"] = last_bpm
        new_section["changeBPM"] = True

        bpm_change_index += 1
        next_bpm_time = (
            time_changes[bpm_change_index]["time"]
            if bpm_change_index < len(time_changes)
            else None
        )
    else:
        new_section["bpm"] = last_bpm
        new_section["changeBPM"] = False

    psych_chart["song"]["notes"].append(new_section)

with open(f"{songNameLol}.json", "w") as f:
    json.dump(psych_chart, f, indent=4)

print("Successfully converted " + psych_chart["song"]["song"] + " to Psych Engine Format!")
input("Press Enter to exit...")
