from refs import config


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
    expected={'titles.protected_terms':['AI','GPT-4','LaTeX','PhD','Python','R','nbgrader','pH','MIT'], 'keys.stopwords':['a','an','and','for','in','of','on','or','the','to','with','your','IS'], 'titles.minor_words':['a','an','and','as','at','but','by','for','in','nor','of','on','or','per','so','the','to','up','via','yet','versus'], 'sorting.ignore_leading_articles':['a','an','the','Le']}
    for key,value in expected.items():
        assert report['values'][key]==value
        assert report['origins'][key]=='default+config: '+str(path)
    assert len(report['values']['titles.protected_terms'])==9
