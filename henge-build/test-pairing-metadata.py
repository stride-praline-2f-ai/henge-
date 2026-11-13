"""Execute the actual integration metadata writer against isolated plists."""
from pathlib import Path
import json,plistlib,subprocess,sys,tempfile
root=Path(__file__).resolve().parent
script=(root/'integrate-upstream.sh').read_text()
marker='python3 - "$source_dir/ios/Henge/Info.plist" "$manifest" <<\'PY\'\n'
writer=script.split(marker,1)[1].split('\nPY\n',1)[0]
manifest=json.loads((root/'manifest.json').read_text())
for modes in ([],['audio'],['audio','processing','processing']):
 with tempfile.TemporaryDirectory() as folder:
  base=Path(folder);app=base/'ios/Henge/Info.plist';helper=base/'ios/HengeJITHelper/Info.plist'
  app.parent.mkdir(parents=True);helper.parent.mkdir(parents=True)
  app.write_bytes(plistlib.dumps({'UIBackgroundModes':modes,'Untouched':'keep','CFBundleShortVersionString':'0.0','CFBundleVersion':'0'}));helper.write_bytes(plistlib.dumps({'Untouched':'helper'}))
  subprocess.run([sys.executable,'-',str(app),str(root/'manifest.json')],input=writer,text=True,check=True)
  actual=plistlib.loads(app.read_bytes());other=plistlib.loads(helper.read_bytes())
  assert actual['UIBackgroundModes'].count('processing')==1
  assert set(actual['UIBackgroundModes'])==set(modes)|{'processing'}
  assert actual['BGTaskSchedulerPermittedIdentifiers']==['$(PRODUCT_BUNDLE_IDENTIFIER).pairing.*']
  assert actual['Untouched']=='keep' and other['Untouched']=='helper'
  assert actual['CFBundleVersion']==other['CFBundleVersion']==manifest['app_build']
print('PASS actual integration metadata: JIT processing retained once, existing audio preserved, pairing-only IDs, versions and unrelated keys retained')
