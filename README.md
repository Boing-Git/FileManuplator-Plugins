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
