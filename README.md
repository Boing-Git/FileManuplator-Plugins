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

## Syntax Guide: Every Character Explained (For Absolute Beginners)

Never written code before? No problem! FileManipulator plugins are essentially just text files that give instructions. However, because computers are very literal, you must use specific punctuation marks (syntax) so the app understands what you mean. 

If you are creating or modifying a plugin for your project, you **must** use these characters exactly as described. If you miss a single quote or bracket, the plugin will fail to load!

### 1. `[ ]` (Single Brackets) vs `[[ ]]` (Double Brackets)
* **Example:** `[plugin]` vs `[[pipeline.process]]`
* **What it means:** Brackets are used to create "Categories" or "Headers". 
* **When to use it:** 
  * Use **Single Brackets `[ ]`** when you are defining something that only happens *once* in the file. For example, `[plugin]` holds the name and description of your plugin. There is only one name, so it gets single brackets.
  * Use **Double Brackets `[[ ]]`** when you are creating a *list of steps*. A conversion pipeline has Step 1, Step 2, Step 3, etc. Every time you start a new step, you **must** write `[[pipeline.process]]`. This tells the engine: *"Here begins the next step in my pipeline list."*
* **Should you use it?** Yes, it is mandatory.

### 2. `.` (The Dot / Period)
* **Example:** `pipeline.process` or `{file.name}`
* **What it means:** The dot means "belongs to" or "inside of".
* **When to use it:** When writing `[[pipeline.process]]`, the dot tells the app that the `process` steps belong *inside* the main `pipeline`. When writing `{file.name}`, it tells the app you want the `name` that belongs to the `file`.
* **Should you use it?** Yes, you must write it exactly as shown. `pipeline process` (with a space) will crash the app.

### 3. `=` (The Equals Sign)
* **Example:** `action = "copy"`
* **What it means:** It assigns a value to a setting. Think of it like filling out a form where the left side is the question, and the right side is your answer.
* **When to use it:** Whenever you need to define a setting. The word on the left (e.g., `action`) is the setting the engine is looking for, and the word on the right (e.g., `"copy"`) is your choice.
* **Should you use it?** Yes, always use a single `=` to give a setting its value.

### 4. `" "` (Double Quotes)
* **Example:** `"magick"` or `"3900M"`
* **What it means:** Double quotes tell the computer: *"This is a piece of text, read it exactly as written."* (In coding, this is called a String).
* **When to use it:** You must wrap almost everything on the right side of the `=` in double quotes. 
  * **Exceptions:** Pure numbers (like `step = 1`) do NOT need quotes. But if a number has letters in it (like `"3900M"` for 3900 Megabytes), it counts as text and **must** have double quotes.
* **Should you use it?** Yes! If you forget the double quotes around text, the app will instantly crash.

### 5. `[ , ]` (Square Brackets with Commas)
* **Example:** `mime_types = ["image/png", "image/jpeg"]`
* **What it means:** This creates a list of multiple items on a single line. The comma `,` separates the items.
* **When to use it:** When a setting can have more than one answer. For example, your plugin might accept both PNG and JPEG images.
* **Should you use it?** Yes, whenever providing a list of accepted file types.

### 6. `{ }` (Curly Braces)
* **Example:** `{file.path}`
* **What it means:** This is a "Fill in the blank" variable.
* **When to use it:** You don't know the name of the file the user will drag into the app. By writing `{file.path}`, you are telling FileManipulator: *"Right before you run this step, delete `{file.path}` and replace it with the actual location of the dropped file."*
* **Should you use it?** Yes, absolutely. Without curly braces, the app will literally look for a file named "file.path" on your hard drive and fail.

### 7. `' '` (Single Quotes inside Double Quotes)
* **Example:** `args = "'{file.path}' -resize 50%"`
* **What it means:** This protects file paths that have spaces in them.
* **When to use it:** If a user drags a file named `my summer vacation.mp4` into the app, the computer's terminal will see three different files (`my`, `summer`, and `vacation.mp4`) because spaces separate commands. Wrapping the path in single quotes `'my summer vacation.mp4'` tells the terminal it is all one single file.
* **Should you use it?** Yes! Because you are already using double quotes `"` around your `args` text, you **must** use single quotes `'` around `{file.path}` or `{output.path}` so the app doesn't break when a file has spaces in its name.

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
