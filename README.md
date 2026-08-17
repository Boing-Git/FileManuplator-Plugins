# FileManipulator Plugin System

FileManipulator supports simple, declarative TOML plugins. Anyone can create powerful custom conversion pipelines by simply explaining the steps the file needs to go through.

Drop any `.toml` file into `~/.local/share/filemanuplator/plugins/` and it will instantly become available as a conversion target.

## Structure of a TOML Plugin

A basic plugin requires a `plugin` metadata table, a `target` name, the `mime_types` it accepts, and a `pipeline` definition containing process steps.

```toml
[plugin]
name = "Discord Split"
version = "1.0"
description = "Splits large files into chunks"

target = "discord_split"
mime_types = ["*/*"]

[[pipeline.process]]
step = 1
action = "split_bytes"
chunk_size = "24M"
output_pattern = "{output.dir}/{file.name}.part"
```

## Syntax Guide: Every Character Explained

To write or modify these plugins for your projects, you must use these specific characters exactly as shown, because Rust's TOML parser is extremely strict. Here is a character-by-character breakdown:

### 1. `[ ]` vs `[[ ]]` (Brackets)
* **Example:** `[plugin]` vs `[[pipeline.process]]`
* **What it does:** Single brackets `[ ]` create a static category (a "Table"). Double brackets `[[ ]]` create an **Array of Tables**. 
* **When to use it:** Use single brackets for one-off definitions like `[plugin]`. Because a conversion pipeline consists of a sequential list of steps (Step 1, Step 2), you **must** use double brackets for `[[pipeline.process]]`. Every time you write `[[pipeline.process]]`, you tell the engine: *"Here is the next step in my pipeline."*
* **Should you use it in your project?** Yes. If you use single brackets for a pipeline step, the parser will crash.

### 2. `.` (The Dot)
* **Example:** `pipeline.process`
* **What it does:** Defines hierarchy. 
* **When to use it:** Use it to tell the parser that the `process` array specifically belongs inside the parent `pipeline` namespace.
* **Should you use it in your project?** Yes. You must use it exactly like this so the Rust `Plugin` struct knows where to find your actions.

### 3. `=` (The Equals Sign)
* **Example:** `action = "split_bytes"`
* **What it does:** It is the assignment operator. 
* **When to use it:** The word on the left is the key the engine looks for, and the word on the right is the value you give it. 
* **Should you use it in your project?** Yes, it is mandatory to assign properties.

### 4. `" "` (Double Quotes)
* **Example:** `"magick"` or `"3900M"`
* **What it does:** It defines a String (text). TOML requires all text to be wrapped in double quotes. 
* **When to use it:** Wrap any text, paths, or arguments in double quotes. Numbers (like `step = 1`) do not need quotes, but if a number contains letters (like `"3900M"`), it instantly becomes text and must have double quotes.
* **Should you use it in your project?** Yes. If you forget them around text, the TOML parser will instantly fail.

### 5. `{ }` (Curly Braces)
* **Example:** `{file.path}`
* **What it does:** FileManipulator's custom variable injection syntax. 
* **When to use it:** When you construct file paths, directories, or commands. The Rust engine dynamically replaces `{file.path}` with the actual path of the file the user dropped into the GUI.
* **Should you use it in your project?** Yes. You must use these when constructing terminal commands, or else the plugin won't know which file to process.

### 6. `' '` (Single Quotes inside Double Quotes)
* **Example:** `args = "'{file.path}' -resize 50%"`
* **What it does:** Terminal shell safety. 
* **When to use it:** If a user drops a file named `my cool video.mp4` (which has spaces), the terminal will see three separate files unless it is wrapped in quotes. Because you are already using double quotes `"` to define the TOML string, you place single quotes `'` inside them.
* **Should you use it in your project?** Yes, always wrap `{file.path}` or `{output.path}` in single quotes when passing them to command-line actions like `ffmpeg` or `magick` to prevent the app from breaking on files with spaces.

## Available Variables
You can inject the following variables directly into your strings (like conditions, destinations, or commands) by wrapping them in `{}` brackets:

* `{file.path}` : The absolute path to the input file.
* `{file.name}` : The full file name (e.g. `movie.part1.mp4`).
* `{file.stem}` : The name without the extension (e.g. `movie.part1`).
* `{file.ext}` : The file extension (e.g. `mp4`).
* `{file.size}` : The exact size of the input file in bytes.
* `{file.mime}` : The detected MIME type (e.g. `video/mp4`).
* `{file.dir}`  : The directory containing the input file.
* `{output.path}`: The requested absolute output file path.
* `{output.dir}` : The requested output directory path.

## Supported Actions

Every action can optionally include a `condition` string. If the condition evaluates to `False`, the action is skipped. Conditions are evaluated using basic numeric logic (e.g., `"{file.size} > 40000"`).

### Built-in Engines
Run commands directly against built-in engines. Just provide the arguments (no need to specify the base command like `ffmpeg`):
* `ffmpeg`
* `magick`
* `pandoc`
* `wkhtmltopdf`
* `chdman`
* `par2`

**Example:**
```toml
[[pipeline.process]]
step = 1
action = "magick"
args = "'{file.path}' -resize 50% '{output.path}'"
```

### `copy`
Copies the input file to a destination.
```toml
[[pipeline.process]]
step = 1
action = "copy"
destination = "{output.path}"
```

### `split_bytes`
Splits a massive file into smaller byte chunks. The `chunk_size` can be specified in bytes, or with suffixes (`4G`, `3900M`, `2K`).
```toml
[[pipeline.process]]
step = 1
action = "split_bytes"
chunk_size = "3900M"
output_pattern = "{output.dir}/{file.name}.part"
```

### `join_bytes`
Automatically globs naturally-ordered split files (like `.part1`, `.part2`) and stitches them back together deterministically.
```toml
[[pipeline.process]]
step = 1
action = "join_bytes"
```

### `checksum`
Generates a hash of the file.
```toml
[[pipeline.process]]
step = 1
action = "checksum"
algorithm = "sha256"
destination = "{output.dir}/{file.name}.sha256"
```

### `regex_copy`
Copies a file while modifying its name via a series of Regex replacements. *(Note: Must be implemented according to the Rust engine's schema if supported)*

### `write_text`
Writes text to a file, and can optionally make the file executable.
```toml
[[pipeline.process]]
step = 1
action = "write_text"
target_path = "{output.dir}/script.sh"
text = "echo 'Hello World'\n"
executable = true
```

### `delete`
Deletes a file (useful for cleaning up temporary scripts or old chunks after a pipeline).
```toml
[[pipeline.process]]
step = 1
action = "delete"
target_path = "{file.dir}/temp.txt"
```
