# ezrclone
A rclone wrapper written in python3 to provide a svn/git like interface.

## Usage

### Initializing ezrclone

`ezrclone init` initializes current directory as the root of the sync. Modify `.rclone-helper/config.json` to match your own configuration.

Example configuration
```JSON
{
  "exclude": [
    "/Shared with me/",
    "/Icon*",
    ".DS_Store"
  ],
  "remote": {
    "onedrive": {
      "flags": ["--ignore-size"],
      "dir": "/" //remote directory
    },
    "gdrive": {
      "flags": [],
      "dir": "/sync"
    }
  },
  "bin": "rclone"
}
```

### Adding file

`ezrclone add <file-list>` stage files for push, pull.

Examples:

`ezrclone add .` adds the current directory.

`ezrclone add *` adds all non-hidden files in the current directory.

`ezrclone add --all` adds all files in the current root.

If you did something wrong (adding files you should not add) use:

`ezrclone reset` and add files again.

### Pushing

`ezrclone push <remote>` pushes files to remote.

Examples:

`ezrclone push onedrive` pushes files to onedrive. (Please first put onedrive in config file and set up rclond to use onedrive).

By default, ezrclone will dry-run once and then ask for confirmation.

`ezrclone -y push onedrive` pushes files to onedrive, skipping dry-run.

`ezrclone -q push onedrive` silently pushes files to onedrive, disabling stdout and stderr.

### Pulling

`ezrclone pull <remote>` pulls files from remote

Examples:

Same as pushing.
