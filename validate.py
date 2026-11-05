#!/usr/bin/env python3
"""
插件清单校验：在推送 plugins.json 之前跑一次。

出过的事故：http-lab 的 HTML 里调了 GD.sidebar.setTitle()，
但清单 permissions 漏了 ui.sidebarTitle —— 安装后一点开就抛
「扩展未声明该能力」，而且错误发生在 opaque iframe 里，很难查。

本脚本从插件源码里抽出所有 GD.* 调用，反查所需权限，
顺带校验文件存在、id 唯一、菜单引用的命令确实注册过。

用法：python validate.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# SDK 方法 -> 宿主能力名（与 js/ext-sdk.js 里的 call('...') 对应）
CAP = {
    'files.list': 'files.list', 'files.read': 'files.read',
    'files.write': 'files.write', 'files.open': 'files.open',
    'files.stat': 'files.stat', 'files.remove': 'files.delete',
    'net.fetch': 'net.fetch', 'net.github': 'net.github',
    'net.grants': 'net.grants', 'net.revoke': 'net.revoke',
    'window.open': 'ui.window', 'window.popout': 'ui.popout',
    'window.close': 'ui.close', 'window.setTitle': 'ui.setTitle',
    'window.fullscreen': 'ui.fullscreen',
    'sidebar.setTitle': 'ui.sidebarTitle',
    'sidebar.badge': 'ui.sidebarBadge',
    'sidebar.show': 'ui.sidebarShow', 'sidebar.hide': 'ui.sidebarHide',
    'commands.register': 'ui.commandRegister',
    'commands.unregister': 'ui.commandUnregister',
    'commands.execute': 'ui.commandExecute',
    'commands.list': 'ui.commandList',
    'menus.contribute': 'ui.menuContribute',
    'storage.get': 'storage.get', 'storage.set': 'storage.set',
    'storage.remove': 'storage.remove', 'storage.keys': 'storage.keys',
    'storage.sync': 'storage.sync', 'storage.restore': 'storage.restore',
    'status.set': 'ui.status', 'status.clear': 'ui.status',
    'ui.toast': 'ui.toast', 'ui.notify': 'ui.notify',
    'ui.progress': 'ui.progress', 'ui.navigate': 'ui.navigate',
    'selection.get': 'selection.get',
    'clipboard.read': 'clipboard.read', 'clipboard.write': 'clipboard.write',
    'theme.get': 'theme.get', 'i18n.t': 'i18n.t', 'i18n.lang': 'i18n.lang',
    'host.info': 'host.info',
}

problems = []
manifest = json.load(open(os.path.join(ROOT, 'plugins.json'), encoding='utf-8'))
plugins = manifest.get('plugins', [])
ids = [p['id'] for p in plugins]
for i, pid in enumerate(ids):
    if ids.index(pid) != i:
        problems.append('重复 id: ' + pid)

for p in plugins:
    pid = p['id']
    rel = p.get('file', '')
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        problems.append('%s: 文件不存在 %s' % (pid, rel))
        continue
    src = open(path, encoding='utf-8').read()

    if p.get('api') == 2:
        have = set(p.get('permissions') or [])
        calls = set(re.findall(r'GD\.([A-Za-z]+)\.([A-Za-z]+)', src))
        need = {CAP[a + '.' + b] for a, b in calls if a + '.' + b in CAP}
        missing = sorted(need - have)
        if missing:
            problems.append('%s: 权限漏声明 %s' % (pid, ', '.join(missing)))

        registered = set(re.findall(
            r'commands\.register\(\s*[\'"]([^\'"]+)[\'"]', src))
        declared = {c['id'] for c in
                    (p.get('contributes', {}).get('commands') or [])}
        menus = {m['command'] for m in
                 (p.get('contributes', {}).get('menus', {}).get('file') or [])}
        dangling = sorted((declared | menus) - registered)
        if dangling:
            problems.append('%s: 菜单/清单引用了未注册的命令 %s'
                            % (pid, ', '.join(dangling)))

if problems:
    print('❌ 校验失败：')
    for x in problems:
        print('   -', x)
    sys.exit(1)
print('✅ 校验通过：%d 个插件，文件齐全、权限与命令引用一致'
      % len(plugins))
