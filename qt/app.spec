# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_submodules
block_cipher = None
all_hidden_imports = collect_submodules('gore2')
print (all_hidden_imports)

a = Analysis(['app.py'],
             pathex=[],
             binaries=[],
             datas=[('splash.png','.')],
             hiddenimports=all_hidden_imports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='Gore Sim Eye',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
app = BUNDLE(exe,
             name='Gore Sim Eye.app',
             icon=None,
             bundle_identifier=None)
