import pytest

from refs.results import RefError
from refs.sources import patch_path


def test_date_member_replaces_whole_array():
    value={'metadata':{'issued':{'date-parts':[[2017,12,5]]}}}
    patch_path(value,'metadata.issued.date-parts',[[2017]],clear=False)
    assert value['metadata']['issued']['date-parts']==[[2017]]
    patch_path(value,'metadata.issued.date-parts',None,clear=True)
    assert value['metadata']['issued']=={}
    for path in ('metadata.issued.date-parts.0','metadata.issued.unknown','metadata.author.0.family','metadata.title.invalid'):
        with pytest.raises(RefError):
            patch_path(value,path,'invalid',clear=False)
