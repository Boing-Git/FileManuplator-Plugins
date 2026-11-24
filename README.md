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
* **What it means:** Quotes group several words into one argument.
* **Do you need them for file paths?** **No.** FileManipulator splits your `args` into arguments *before* filling in the variables, so `{file.path}` is always one single argument even when the file is called `my summer vacation.mp4`. Writing `-i {file.path}` and `-i '{file.path}'` do exactly the same thing.
* **When they are still useful:** when *you* want to write several words as one argument, e.g. `-metadata "title=My Film"`.
* **Safety note:** because arguments are never handed to a shell, characters like `;`, `|`, `$` and `&` in a file name or in something you type into a plugin's form are ordinary text. They cannot run commands.

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

## Tabs, widgets and colours

A plugin can also have its own tab (`[tab]`) with widgets (`[[ui]]`): file pickers, sliders, an image cropping canvas, an `html_view` that runs a web page, a `notice` for warnings, and more. Any widget can take a colour role, e.g. `color = "error"` for something destructive; roles follow the colour scheme the user picked. All widgets and roles are described in the [filemanuplator README](https://github.com/Boing-Git/FileManuplator#3-declarative-ui-widgets-ui).

`html_runner.toml` is the smallest example: a file picker and an `html_view`, with no pipeline at all.

## Running on phones

The mobile app has these plugins built in. A phone has no external programs, so a plugin whose pipeline uses `exec`, `ffmpeg`, `magick`, `pandoc`, `wkhtmltopdf`, `chdman` or `par2` is shown there as desktop-only. Every other action runs on the phone too. The phone saves one result per run: the file the pipeline wrote to `{output.path}`.

## Supported Actions

Every action can optionally include a `condition` string. If the condition is false, the action is skipped. A condition that cannot be parsed stops the pipeline with an error naming the step.

### Conditions

```toml
condition = "{file.size} > 40000"
condition = "'{file.mime}'.startswith('image/') or '{file.mime}'.startswith('video/')"
condition = "'{file.ext}' in ['png', 'jpg'] and {file.size} >= 1024"
condition = "not ('{file.ext}' == 'txt')"
```

* Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`. If both sides are numbers they are compared as numbers, otherwise as text.
* Text functions: `.startswith('x')`, `.endswith('x')`, `.contains('x')`.
* Membership: `value in ['a', 'b']` and `value not in ['a', 'b']`.
* Combine with `and`, `or`, `not` and parentheses. `and` binds tighter than `or`.
* Text must be quoted (`'...'` or `"..."`). Variables such as `{file.size}` and widget ids like `{quality}` can be used inside quotes or on their own.
* Note that `{file.ext}` has **no leading dot** (`pdf`, not `.pdf`), and for `archive.tar.gz` it is just `gz`.

### `exec` — run any program (recommended)
Runs a program with an explicit list of arguments. Nothing is passed through a shell.
```toml
[[pipeline.process]]
step = 1
action = "exec"
program = "ffmpeg"
argv = ["-y", "-i", "{file.path}", "-vcodec", "libx264", "{output.path}"]
```
Each entry of `argv` is exactly one argument, so spaces and punctuation inside a variable are always safe. If the program is not installed, the plugin stops with a message naming it instead of a bare exit code.

### Built-in Engines
Shorthand for programs FileManipulator expects to be available. Provide the arguments only — the program name is implied:
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
args = "{file.path} -resize 50% {output.path}"
```

The `args` string is split into arguments on spaces (quotes group words together), and only then are `{variables}` filled in. That ordering is what keeps values inert — see the note on quotes above.

### `export_image` — crop, fit and compress an image (built in)
Does everything in one pass, so a JPEG is compressed only once. Every setting except the two files is optional, and it needs no external program, so it also runs on phones.
```toml
[[pipeline.process]]
step = 1
action = "export_image"
target_file = "{file.path}"
output_file = "{output.path}"
crop_data = "{preview_canvas.crop_data}"   # WxH+X+Y, e.g. from an image_canvas
width = "{width}"
height = "{height}"
fit = "{fit_mode}"                          # contain (default), cover or stretch
max_kb = "{target_size}"
```
* `fit`: **contain** keeps the whole picture inside `width` × `height`, **cover** fills it exactly and trims the overflow, **stretch** fills it exactly and distorts.
* `max_kb`: picks the highest JPEG quality whose file fits in that many KiB. It only applies when the output is a JPEG; lossless formats are saved as they are.
* The output format comes from the output file's extension (or `format = "png"`).

### `copy`
Copies the input file to a destination.
```toml
[[pipeline.process]]
step = 1
action = "copy"
destination = "{output.path}"
```

### `split_bytes`
Splits a massive file into smaller byte chunks. The `chunk_size` can be given in bytes or with a suffix (`4G`, `3900M`, `2K`). Chunks are written as `<output_pattern>00`, `<output_pattern>01`, and so on.
```toml
[[pipeline.process]]
step = 1
action = "split_bytes"
chunk_size = "3900M"
output_pattern = "{output.dir}/{file.name}.part"
```

### `join_bytes`
Finds the sibling `.part*` files, sorts them in natural order (so `.part2` comes before `.part10`), and stitches them back together.
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
Copies the file into `{output.dir}`, renaming it by applying a list of regex replacements to the file name in order. Replacements may use variables such as `{file.ext}`.
```toml
[[pipeline.process]]
step = 1
action = "regex_copy"

[[pipeline.process.rules]]
pattern = "\\."
replacement = " "

[[pipeline.process.rules]]
pattern = "\\b(1080p|x264)\\b.*"
replacement = ""
```

### `split_csv`
Splits a CSV into chunks of `chunk_size` rows, repeating the header row in every chunk. Files are written as `<output_pattern>000.csv`, `<output_pattern>001.csv`, ...
```toml
[[pipeline.process]]
step = 1
action = "split_csv"
chunk_size = "100000"
output_pattern = "{output.dir}/{file.stem}_part_"
```

### `join_csv`
Joins `<prefix>_part_000.csv`, `<prefix>_part_001.csv`, ... back into one CSV, keeping a single header. `<prefix>` is the input path up to `_part_`.
```toml
[[pipeline.process]]
step = 1
action = "join_csv"
```

### `echo`
Prints `value` (variables allowed) to the application log. Handy while developing a plugin.
```toml
[[pipeline.process]]
step = 1
action = "echo"
value = "Processing {file.name} ({file.size} bytes)"
```

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
