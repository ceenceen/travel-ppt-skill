# -*- coding: utf-8 -*-
"""通过 GitHub REST API 推送（git smart-HTTP 被代理重置时的兜底方案）。
仅上传相对父 commit 变化的文件；未变文件复用父 tree 的 blob sha（不重传）。
用法: GITHUB_PAT=xxx python push_api.py
"""
import os, sys, json, base64, subprocess, tempfile

import requests

API = 'https://api.github.com'
OWNER = 'ceenceen'
REPO = 'travel-ppt-skill'
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PAT = os.environ.get('GITHUB_PAT')
if not PAT:
    print('NO GITHUB_PAT'); sys.exit(2)

sess = requests.Session()
sess.headers.update({
    'Authorization': f'Bearer {PAT}',
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'travel-ppt-skill-push',
})


def gh(method, path, json_body=None, timeout=120):
    r = sess.request(method, API + path, json=json_body, timeout=timeout)
    if r.status_code >= 400:
        print(f'HTTP {r.status_code} {method} {path}: {r.text[:300]}')
        sys.exit(3)
    return r


def git(*args):
    return subprocess.run(['git'] + list(args), cwd=REPO_DIR,
                           capture_output=True, text=True, check=True).stdout.strip()


# 1) 当前 main
ref = gh('GET', f'/repos/{OWNER}/{REPO}/git/refs/heads/main').json()
main_sha = ref['object']['sha']
commit = gh('GET', f'/repos/{OWNER}/{REPO}/git/commits/{main_sha}').json()
tree_sha = commit['tree']['sha']
parent_tree = gh('GET', f'/repos/{OWNER}/{REPO}/git/trees/{tree_sha}?recursive=1').json()
parent = {e['path']: e['sha'] for e in parent_tree.get('tree', []) if e['type'] == 'blob'}
print(f'main={main_sha[:10]} parent_blobs={len(parent)}')

# 2) 枚举本地要纳入的文件（直接遍历目录，避免 git status 的中文引号转义问题）
SKIP_DIRS = {'.git', '__pycache__', 'spot_gallery'}
def keep(p):
    if p.startswith('.git/') or '/.git/' in p:
        return False
    parts = p.split('/')
    if any(s in SKIP_DIRS for s in parts):
        return False
    if p.endswith('pexels_key.txt'):
        return False
    res = subprocess.run(['git', 'check-ignore', p], cwd=REPO_DIR,
                          capture_output=True, text=True)
    if res.returncode == 0:  # ignored
        return False
    return True

local_paths = []
for root, dirs, files in os.walk(REPO_DIR):
    if '.git' in dirs:
        dirs.remove('.git')
    for d in list(dirs):
        if d in SKIP_DIRS:
            dirs.remove(d)
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, REPO_DIR).replace(os.sep, '/')
        if keep(rel):
            local_paths.append(rel)
local_paths.sort()

print(f'local files to include: {len(local_paths)}')

# 3) 计算 blob sha；变化的上传，未变复用父 sha
tree_entries = {}
uploaded = 0
reused = 0
for p in local_paths:
    lsha = git('hash-object', p)
    if p in parent and parent[p] == lsha:
        tree_entries[p] = lsha
        reused += 1
        continue
    data = open(os.path.join(REPO_DIR, p), 'rb').read()
    b64 = base64.b64encode(data).decode('ascii')
    # 大文件单独设超时
    t = 300 if len(data) > 5_000_000 else 120
    res = gh('POST', f'/repos/{OWNER}/{REPO}/git/blobs',
             {'content': b64, 'encoding': 'base64'}, timeout=t)
    tree_entries[p] = res.json()['sha']
    uploaded += 1
    print(f'  upload {p} ({len(data)//1024}KB)')

print(f'uploaded={uploaded} reused={reused}')

# 4) 创建 tree
tree_payload = [{'path': p, 'mode': '100644', 'type': 'blob', 'sha': s}
                for p, s in tree_entries.items()]
new_tree = gh('POST', f'/repos/{OWNER}/{REPO}/git/trees', {'tree': tree_payload}).json()
print(f'new tree={new_tree["sha"][:10]} entries={len(tree_payload)}')

# 5) 创建 commit
msg = 'feat: add Mode C · Spot Gallery (Pexels fetch w/ global dedup + perceptual-hash 2nd pass, dark grid layout w/ arrival-day tags) + sample'
new_commit = gh('POST', f'/repos/{OWNER}/{REPO}/git/commits',
                {'message': msg, 'tree': new_tree['sha'], 'parents': [main_sha]}).json()
print(f'new commit={new_commit["sha"][:10]}')

# 6) 更新 ref
gh('PATCH', f'/repos/{OWNER}/{REPO}/git/refs/heads/main',
   {'sha': new_commit['sha'], 'force': False})
print('PUSH_OK -> main updated')
