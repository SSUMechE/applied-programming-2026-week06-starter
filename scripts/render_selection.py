"""Draw the actual stored raw/final winner, never a hardcoded answer."""
import json
from pathlib import Path
data = json.loads(Path("artifacts/candidate_comparison.json").read_text(encoding="utf-8"))
low,high = data["scene"]["bounds"]["lower"],data["scene"]["bounds"]["upper"]
scale = min(600/(high[0]-low[0]),320/(high[1]-low[1]))
def screen(xy):
    return (40+scale*(xy[0]-low[0]),365-scale*(xy[1]-low[1]))
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="440">',
         '<rect width="940" height="440" fill="white"/>',
         '<g fill="black" font-family="Times New Roman" font-size="18">',
         '<text x="25" y="30">Stored selected route: raw and shortened (metres)</text>']
for obstacle in data["scene"]["obstacles"]:
    x,y = screen(obstacle["center_xy"])
    r = scale*obstacle["radius_m"]
    parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#dddddd" stroke="black"/>')
selected = data["selected_id"]
if selected is not None:
    record = data["candidates"][selected]
    for points,width,dash in ((record["shortening"]["raw_path_xy"],2,' stroke-dasharray="7 5"'),
                              (record["path_xy"],4,'')):
        vertices = " ".join(f"{x},{y}" for x,y in map(screen,points))
        parts.append(f'<polyline points="{vertices}" fill="none" stroke="black" stroke-width="{width}"{dash}/>')
    parts.append(f'<text x="660" y="120">Selected: {selected}</text>')
    for row,key in enumerate(("raw_length_m","final_length_m")):
        parts.append(f'<text x="660" y="{160+row*35}">{key}: {record["shortening"][key]:.3f}</text>')
else:
    parts.append('<text x="660" y="120">No accepted route</text>')
parts.append(f'<text x="25" y="410">Dashed: raw. Solid: shortened. All {len(data["results"])} records remain in JSON.</text>')
parts.append('</g></svg>')
destination = Path("artifacts/candidate_selection.svg")
destination.write_text("".join(parts),encoding="utf-8")
print(f"saved={destination.as_posix()}")
