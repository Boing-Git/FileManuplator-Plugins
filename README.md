# filemanuplator Plugin System

filemanuplator supports simple, declarative YAML plugins. Anyone can create powerful custom conversion pipelines by simply explaining the steps the file needs to go through.

Drop any `.yaml` file into `~/.local/share/filemanuplator/plugins/` and it will instantly become available as a conversion target.

## Structure of a YAML Plugin

A basic plugin requires a `target` name, the `mime_types` it accepts, and a list of `actions`. 
**Note:** You can place multiple plugin definitions in a single YAML file by structuring it as a list!

```yaml
- target: discord_split
  mime_types: 
    - "*/*"
  description: "Splits large files into chunks"
  actions:
    - type: split_bytes
      chunk_size: "24M"
      output_pattern: "{output.dir}/{file.name}.part"

- target: discord_join
  mime_types: ["*/*"]
  description: "Joins chunks back together"
  actions:
    - type: join_bytes
```

## Available Variables
You can inject the following variables directly into your strings (like conditions, destinations, or commands) by wrapping them in `{}` brackets:

* `{file.path}` : The absolute path to the input file.
* `{file.name}` : The full file name (e.g. `movie.part1.mp4`).
* `{file.stem}` : The name without the extension (e.g. `movie.part1`).
* `{file.ext}` : The file extension (e.g. `.mp4`).
* `{file.size}` : The exact size of the input file in bytes.
* `{file.mime}` : The detected MIME type (e.g. `video/mp4`).
* `{file.dir}`  : The directory containing the input file.
* `{output.path}`: The requested absolute output file path.
* `{output.dir}` : The requested output directory path.

## Supported Actions

Every action can optionally include a `condition` string. If the condition evaluates to `False`, the action is skipped. Conditions are evaluated using standard Python math logic (e.g., `"{file.size} > 40000"`).

### Built-in Engines
Run commands directly against built-in engines. Just provide the arguments (no need to specify the base command like `ffmpeg`):
* `ffmpeg`
* `magick`
* `pandoc`
* `wkhtmltopdf`
* `chdman`
* `par2`

**Example:**
```yaml
- type: magick
  args: "'{file.path}' -resize 50% '{output.path}'"
```

### `copy`
Copies the input file to a destination.
```yaml
- type: copy
  destination: "{output.path}"
```

### `split_bytes`
Splits a massive file into smaller byte chunks. The `chunk_size` can be specified in bytes, or with suffixes (`4G`, `3900M`, `2K`).
```yaml
- type: split_bytes
  chunk_size: "3900M"
  output_pattern: "{output.dir}/{file.name}.part"
```

### `join_bytes`
Automatically globs naturally-ordered split files (like `.part1`, `.part2`) and stitches them back together deterministically.
```yaml
- type: join_bytes
```

### `checksum`
Generates a hash of the file.
```yaml
- type: checksum
  algorithm: "sha256"
  destination: "{output.dir}/{file.name}.sha256"
```

### `regex_copy`
Copies a file while modifying its name via a series of Regex replacements.
```yaml
- type: regex_copy
  rules:
    - pattern: "\\."
      replacement: " "
    - pattern: "$"
      replacement: "{file.ext}"
```

### `delete`
Deletes a file (useful for cleaning up temporary scripts or old chunks after a pipeline).
```yaml
- type: delete
  target_path: "{file.dir}/temp.txt"
```
