import subprocess


def pull_master():
    subprocess.call(['git', 'pull', 'upstream/master'])


def save_to_git(args, user_config, file):
    if args.no_git:
        return
    subprocess.call(['git', 'add', file])
    if file.is_relative_to('games'):
        subprocess.call(['git', 'commit', '-m', f'{user_config.username} generated new game'])
    else:
        subprocess.call(['git', 'commit', '-m', f'{user_config.username} played a game'])

    subprocess.call(['git', 'push'])
