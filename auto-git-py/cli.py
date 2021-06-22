from pathlib import Path

import click
from pygit2 import (
    discover_repository, 
    Repository,
    Signature
)

@click.group()
@click.pass_context
def main(ctx):
    pass

@main.command()
@click.argument('file_path')
@click.option('-m', '--commit-message', 'message')
@click.option('-c', '--confirm-config', 'confirm', is_flag=True)
@click.option('-b', '--branch', 'branch', default='master')
def commit(file_path, message, confirm, branch):
    repo_path = discover_repository(file_path)
    if not repo_path:
        raise click.exceptions.UsageError(
            f'{file_path} is not in a git repo'
        )
    if not message:
        file_name = Path(file_path).name
        message = f'AUTO COMMIT {file_name.upper()}'
    repo = Repository(repo_path)
    branch = repo.branches[branch]

    user_email = repo.config['user.email']
    user_name = repo.config['user.name']
    if confirm:
        confirmation = click.confirm(
            '\n'.join([
                f'name: {user_name}',
                f'email: {user_email}',
                f'message: {message}',
                f'ref: {branch.branch_name}',
                'Is this correct?'
            ])
        )
        if not confirmation:
            click.echo('commit not confirmed exit')
            click.Abort(0)
    index = repo.index
    index.add(file_path)
    index.write()
    author = Signature(user_name, user_email)
    commiter = Signature(user_name, user_email)
    tree = index.write_tree()
    parent, ref = repo.resolve_refish(refish=branch.branch_name)
    oid = repo.create_commit(
        ref.name, 
        author, 
        commiter, 
        message,
        tree,
        [parent.id]
    )

if __name__ == "__main__":
    main()