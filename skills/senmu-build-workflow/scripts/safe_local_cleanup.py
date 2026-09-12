#!/usr/bin/env python3
"""Bounded cleanup inventory and native trash only. A plan confers no authority."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import time

MAX_ITEMS = 10000
MAX_DEPTH = 32
MAX_SECONDS = 10
MAX_TARGETS = 100


class Rejected(ValueError):
    pass


def checked_path(value):
    raw = str(value)
    if not raw or any(c in raw for c in '*?[]') or any(p in ('.', '..') for p in raw.split('/')):
        raise Rejected('empty, traversal or wildcard path')
    p = Path(raw)
    if not p.is_absolute() or raw.startswith('//'):
        raise Rejected('absolute local path required')
    for part in reversed((p, *p.parents)):
        s = part.lstat()
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 1024:
            raise Rejected('link/reparse ancestor')
    return p


def snapshot(path):
    """No contents read. Any uninspectable descendant rejects the entire target."""
    rows, total = [], 0
    started = time.monotonic()
    device = path.lstat().st_dev

    def visit(p, rel, depth):
        nonlocal total
        if len(rows) >= MAX_ITEMS or depth > MAX_DEPTH or time.monotonic() - started > MAX_SECONDS:
            raise Rejected('incomplete bounded scan')
        s = p.lstat()
        if p.name == '.git' or s.st_dev != device or os.path.ismount(p):
            raise Rejected('repository or mount boundary')
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 1024:
            raise Rejected('link/reparse descendant')
        if not (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)):
            raise Rejected('special file')
        if not s.st_mode & 0o444 or (stat.S_ISDIR(s.st_mode) and not s.st_mode & 0o111):
            raise Rejected('unreadable descendant')
        rows.append([rel, s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns])
        if stat.S_ISDIR(s.st_mode):
            # Do not materialize an unbounded directory listing.
            with os.scandir(p) as entries:
                for entry in entries:
                    visit(Path(entry.path), rel + '/' + entry.name, depth + 1)
        else:
            total += s.st_size
    visit(path, '', 0)
    rows.sort()
    def digest(data):
        return hashlib.sha256(json.dumps(data, separators=(',', ':')).encode()).hexdigest()
    # Renaming into Trash can change ctime; retain inode, mode, size and mtime.
    return {'observed': digest(rows), 'identity': digest([r[:-1] for r in rows]),
            'entries': len(rows), 'logical_bytes': total}


def make_plan(root, targets, authorization):
    root = checked_path(root)
    if root == Path('/') or root == Path.home() or not root.is_dir():
        raise Rejected('unsafe project root')
    if not authorization.strip() or not 0 < len(targets) <= MAX_TARGETS:
        raise Rejected('authority reference and bounded targets required')
    paths = [checked_path(t) for t in targets]
    for p in paths:
        if root not in p.parents or '.git' in p.relative_to(root).parts:
            raise Rejected('outside project or protected Git path')
        if any(p == q or p in q.parents or q in p.parents for q in paths if q is not p):
            raise Rejected('duplicate or overlapping targets')
        for ancestor in p.parents:
            if ancestor == root:
                break
            if (ancestor / '.git').exists() or (ancestor / '.git').is_symlink() or os.path.ismount(ancestor):
                raise Rejected('nested repository or mount ancestor')
        if p.lstat().st_dev != root.lstat().st_dev:
            raise Rejected('cross-volume target')
    s = root.stat()
    return {'schema': 1, 'root': str(root), 'root_identity': [s.st_dev, s.st_ino],
            'authorization': authorization, 'items': [dict(path=str(p), **snapshot(p)) for p in paths],
            'protection_scan': 'complete',
            'retention_reason': 'retain until ownership, retention, authority and writer exclusion are established',
            'backend': 'macOS Foundation (native recovery acceptance pending)' if platform.system() == 'Darwin' else 'unsupported',
            'git_status': 'not_measured; caller must check tracked/untracked/ignored and governed resources',
            'warning': 'No authority or active-writer proof; metadata is not an atomic lock.'}


JXA = r'''ObjC.import('Foundation');
function run(argv) {
  const url = $.NSURL.fileURLWithPath(argv[0]);
  const local = Ref(), checkError = Ref();
  if (!url.getResourceValueForKeyError(local, $.NSURLVolumeIsLocalKey, checkError) || !local[0].boolValue)
    return JSON.stringify({ok:false, error:'local volume not established'});
  const destination = Ref(), error = Ref();
  const ok = $.NSFileManager.defaultManager.trashItemAtURLResultingItemURLError(url, destination, error);
  return JSON.stringify({ok:!!ok, destination: destination[0] ? ObjC.unwrap(destination[0].path) : null,
    error: error[0] ? 'native_error_' + Number(error[0].code) : null,
    cancelled: error[0] ? Number(error[0].code) === 3072 : false});
}'''


def native_trash(path):
    # No remove/unlink/purge API or permanent-delete fallback exists here.
    result = subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', '-e', JXA, str(path)],
                            text=True, capture_output=True, timeout=30, check=True)
    if len(result.stdout) > 8192:
        raise Rejected('oversized backend receipt')
    return json.loads(result.stdout)


def execute(plan, writers_stopped, backend=None):
    if not writers_stopped:
        raise Rejected('writer exclusion must be established before execution')
    if backend is None:
        if platform.system() != 'Darwin' or not Path('/usr/bin/osascript').is_file():
            raise Rejected('native backend unavailable; no fallback')
        backend = native_trash
    if plan.get('schema') != 1:
        raise Rejected('unsupported plan')
    current = make_plan(plan['root'], [i['path'] for i in plan['items']], plan['authorization'])
    if current != plan:
        raise Rejected('plan changed or modified; no backend called')
    results, stopped = [], False
    for item in plan['items']:
        p = Path(item['path'])
        if stopped:
            results.append({'path': str(p), 'status': 'not_called', 'called': False})
            continue
        try:
            # Recheck ancestors and entire tree immediately before each call.
            now = make_plan(plan['root'], [str(p)], plan['authorization'])
            if now['root_identity'] != plan['root_identity'] or now['items'][0] != item:
                raise Rejected('changed after planning')
        except (OSError, ValueError):
            results.append({'path': str(p), 'status': 'rejected_before_call', 'called': False, 'reason': 'target changed or recheck incomplete'})
            stopped = True
            continue
        receipt = {}
        error_kind = None
        try:
            receipt = backend(p)
            if not isinstance(receipt, dict):
                receipt = {}
        except (Exception, KeyboardInterrupt) as error:
            # A timeout/exception can occur after a move. Never retry blindly.
            error_kind = type(error).__name__
        status = 'unknown'
        try:
            if p.exists() and snapshot(checked_path(p))['observed'] == item['observed']:
                status = 'confirmed_retained'
            elif not p.exists() and receipt.get('destination'):
                destination = checked_path(receipt['destination'])
                if snapshot(destination)['identity'] == item['identity']:
                    status = 'confirmed_trashed'
        except (OSError, ValueError):
            pass
        results.append({'path': str(p), 'status': status, 'called': True, 'error': error_kind or receipt.get('error'), 'backend_ok': receipt.get('ok') is True,
                        'cancelled': receipt.get('cancelled') is True,
                        'destination': receipt.get('destination') if status == 'confirmed_trashed' else None})
        stopped = status != 'confirmed_trashed' or receipt.get('ok') is not True or receipt.get('cancelled') is True
    return {'results': results, 'complete': bool(results) and not stopped,
            'disk_bytes_reclaimed': 'not_measured',
            'next_action': 'inspect unknown outcomes; never retry or restore over existing paths automatically' if stopped else 'retain recovery receipt'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('plan')
    p.add_argument('--root', required=True)
    p.add_argument('--authorization', required=True)
    p.add_argument('targets', nargs='+')
    p = sub.add_parser('trash')
    p.add_argument('--plan', required=True)
    p.add_argument('--writers-stopped', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'plan':
            result = make_plan(args.root, args.targets, args.authorization)
        else:
            with open(args.plan) as stream:
                raw = stream.read(131073)
            if len(raw) > 131072:
                raise Rejected('oversized plan')
            result = execute(json.loads(raw), args.writers_stopped)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('complete', True) else 2
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'rejected', 'reason': type(error).__name__}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
