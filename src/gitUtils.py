import subprocess


def save_to_git(args, user_config, file):
    if args.no_git:
        return
    subprocess.call(['git', 'add', file])
    if file.contains('games'):
        subprocess.call(['git', 'commit', '-m', f'"{user_config.username} generated new game"'])
    else:
        subprocess.call(['git', 'commit', '-m', f'"{user_config.username} played a game"'])
