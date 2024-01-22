# `notion_autobot_cli/`

**Usage**:

```console
$ notion_autobot_cli/ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `discord-test`: Test discord webhook.
* `parse`: Parse notion debug dump data.
* `poke`: Poke notion.
* `today`: Generate today's task list markdown report file.

## `notion_autobot_cli/ discord-test`

Test discord webhook.

**Usage**:

```console
$ notion_autobot_cli/ discord-test [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `notion_autobot_cli/ parse`

Parse notion debug dump data.

**Usage**:

```console
$ notion_autobot_cli/ parse [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `notion_autobot_cli/ poke`

Poke notion.

**Usage**:

```console
$ notion_autobot_cli/ poke [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `notion_autobot_cli/ today`

Requests latest data from Notion database and outputs to `debug.json` file. The data is then parsed and written to a template.

**Usage**:

```console
$ notion_autobot_cli/ today [OPTIONS]
```

**Options**:

* `--debug / --no-debug`: Enable debug mode. This is useful when testing locally. When activated, the output is stored in a local .json file, which can be used to test parsing features without making repeated calls to Notion.  [default: no-debug]
* `--all-tasks / --no-all-tasks`: Retrieve tasks of all types  [default: no-all-tasks]
* `--discord / --no-discord`: Post to discord  [default: no-discord]
* `--help`: Show this message and exit.
