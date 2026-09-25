"""Canonical editing keeps stored state separate and validates the final record."""

import pytest
from pydantic import ValidationError

from refs.models import editable, revalidate


def test_editable_record_deep_copies_fields_and_preserves_legacy_key():
    stored={'id':'catalog-id','revision':4,'schema_version':'1.0','citation_key':'paper-2024',
            'loc':None,'metadata':{'title':'Synthetic Paper','author':[{'family':'Smith'}]}}
    draft=editable(stored)
    assert set(draft)=={'schema_version','citation_key','metadata'}
    draft['metadata']['author'][0]['family']='Jones'
    assert stored['metadata']['author'][0]['family']=='Smith'
    assert revalidate(draft)['citation_key']=='paper-2024'
    draft['citation_key']='legacy key'
    assert revalidate(draft)['citation_key']=='legacy key'
    draft['metadata']['title']=''
    with pytest.raises(ValidationError):
        revalidate(draft)
