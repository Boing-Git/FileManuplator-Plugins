import yaml
import toml
import os
import glob

for yml_path in glob.glob("*.yaml"):
    with open(yml_path, "r") as f:
        raw_data = yaml.safe_load(f)
    
    stem = os.path.splitext(yml_path)[0]
    
    if isinstance(raw_data, list):
        data = raw_data[0] if raw_data else {}
        actions = []
        for d in raw_data:
            if isinstance(d, dict) and "actions" in d:
                actions.extend(d["actions"])
    else:
        data = raw_data
        actions = data.get("actions", [])
        
    toml_data = {
        "plugin": {
            "name": data.get("target", stem).replace("_", " ").title(),
            "version": "1.0",
            "description": data.get("description", "No description")
        },
        "target": data.get("target", stem),
        "mime_types": data.get("mime_types", ["*/*"]),
        "pipeline": {
            "process": []
        }
    }
    
    if actions:
        for idx, action in enumerate(actions):
            step = {"step": idx + 1, "action": action.get("type", "unknown")}
            for k, v in action.items():
                if k != "type":
                    step[k] = v
            toml_data["pipeline"]["process"].append(step)
            
    with open(stem + ".toml", "w") as f:
        toml.dump(toml_data, f)
        
    os.remove(yml_path)
