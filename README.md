# Overleaf Backup Tool
>Data is precious, especially for Latex files.

Some people may choose to set up self-hosted [Overleaf](https://github.com/overleaf/toolkit/), 
but its standard [backup](https://github.com/overleaf/overleaf/wiki/Data-and-Backups) can be overwhelming.
Sometimes, you just want to have a simple backup of your *projects*, not users, histories, etc.

## Config
You need to set up a `config.yml` file in the same directory as the script.

```yaml
user:
  email: <Your Email>
  password: <Your Password>
project:
  url: <Self-Hosted Overleaf URL>
  id: <Project ID>
backup:
  download:
    path: <Absolute Path to Store Backup Files>
  git:
    path: <Absolute Path to Store Git Repository>
  rsync:
    server: <Rsync Server>
    port: <Server Port>
    destination: <Destination Path in Rsync Server>
```

Note that:

- `project.url`: The port is necessary if you are using a non-standard port.
- `project.id`: The ID of the project you want to back up.
- `backup`: You should provide at least one of the following:
  - `download`: Download the `zip` into your local path.
  - `git`: Push the files into git repository that you've already set up.
  - `rsync`: Sync with a remote server using `rsync`. The `server` can be either `<user>@<host>` or a host alias in your `~/.ssh/config`.

## Usage

```bash
python3 main.py download
python3 main.py git
python3 main.py rsync
```