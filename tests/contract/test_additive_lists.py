from refs import config, naming


def test_configured_lists_extend_defaults(tmp_path):
    path=tmp_path/'config.toml'
    path.write_text('''schema_version=1
[keys]
stopwords=["IS","the","is"]
[titles]
protected_terms=["MIT","python","mit"]
minor_words=["versus","THE"]
[sorting]
ignore_leading_articles=["Le","THE","le"]
''')
    settings=config.select(str(path),str(tmp_path/'cat'),no_project_config=True)
    report=settings.inspect()
    expected={'titles.protected_terms':naming.GLOBAL_TERMS+['MIT'], 'keys.stopwords':sorted(naming.STOPWORDS)+['IS'], 'titles.minor_words':sorted(naming.MINOR)+['versus'], 'sorting.ignore_leading_articles':['a','an','the','Le']}
    for key,value in expected.items():
        assert report['values'][key]==value
        assert report['origins'][key]=='default+config: '+str(path)
    assert len(report['values']['titles.protected_terms'])==9
