"""One-time loc assignment through the application update boundary."""
import argparse
import json
from pathlib import Path

from refs import resources, sources
from refs.catalog import connect
from refs.config import select
from refs.models import normalize_loc


def preview(settings, box_root):
    box_root=Path(box_root).expanduser().absolute()
    result=[]
    with connect(settings.catalog_path()) as c:
        for row in c.execute('SELECT id,citation_key,revision,loc FROM sources ORDER BY citation_key'):
            item=dict(row)
            files=resources.inventory(c,item['id'])
            folders={}
            managed={}
            for resource in files:
                path=resources.resolve_path(settings,resource)
                if path.is_relative_to(box_root):
                    relative=str(path.parent.relative_to(box_root))
                    if relative!='.':
                        folder=normalize_loc(relative)
                        folders[folder.casefold()]=folder
                elif resource['root']=='library':
                    relative=str(Path(resource['relative']).parent)
                    folder=normalize_loc(relative) if relative!='.' else resources.UNFILED
                    managed[folder.casefold()]=folder
            loc,reason=None,'no files'
            if not files:
                reason='no files'
            elif len(folders)>1:
                reason='multiple Box folders; choose loc explicitly'
            elif folders:
                loc,reason=next(iter(folders.values())),'Box folder'
            elif len(managed)>1:
                reason='multiple managed folders; choose loc explicitly'
            elif managed:
                loc,reason=next(iter(managed.values())),'managed folder'
            else:
                loc,reason=resources.UNFILED,'non-topic storage'
            result.append(dict(source_id=item['id'],citation_key=item['citation_key'],revision=item['revision'],old_loc=item['loc'],loc=loc,reason=reason,state='unchanged' if loc is None or loc==item['loc'] else 'planned'))
    return result


def apply(settings, entries):
    result=[]
    for entry in entries:
        if entry['state']=='planned':
            source=sources.update(settings.catalog_path(),entry['source_id'],{'schema_version':'1.0','set':{'loc':entry['loc']}},entry['revision'],policy=settings.values)
            entry=entry | dict(state='applied',revision=source['revision'])
        result.append(entry)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ['config','catalog','box-root']:
        parser.add_argument('--'+option,required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    settings=select(args.config,args.catalog,no_project_config=True)
    entries=preview(settings,args.box_root)
    if args.execute:
        entries=apply(settings,entries)
    print(json.dumps(dict(dry_run=not args.execute,entries=entries),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
